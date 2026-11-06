# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports):
# - API de proveedores de 19: método de pago "Flow" (payment.method), sin la
#   antigua función de comisiones (eliminada del núcleo en 17; en producción
#   estaba desactivada).
# - Las peticiones a Flow se firman con el cliente de lib/payflow (HMAC-SHA256)
#   y se devuelven como dict para el flujo estándar _process().
import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..lib.payflow.client import Client

_logger = logging.getLogger(__name__)

FLOW_PROD_URL = "https://www.flow.cl/api"
FLOW_TEST_URL = "https://sandbox.flow.cl/api"


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('flow', 'Flow')],
        ondelete={'flow': 'set default'},
    )
    flow_api_key = fields.Char(string="Api Key", required_if_provider='flow', copy=False)
    flow_private_key = fields.Char(
        string="Secret Key", required_if_provider='flow', copy=False, groups='base.group_system')
    flow_payment_method = fields.Selection(
        [
            ('1', 'Webpay'),
            ('2', 'Servipag'),
            ('3', 'Multicaja'),
            ('5', 'Onepay'),
            ('8', 'Cryptocompra'),
            ('9', 'Todos los medios'),
        ],
        string="Medio de pago Flow",
        required=True,
        default='9',
    )

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'flow':
            return super()._get_default_payment_method_codes()
        return {'flow'}

    def _flow_get_api_url(self):
        self.ensure_one()
        return FLOW_PROD_URL if self.state == 'enabled' else FLOW_TEST_URL

    def _flow_send_request(self, method, endpoint, data):
        """Firma y envía una petición a la API de Flow y devuelve la respuesta (dict).

        :raise ValidationError: si Flow no responde o devuelve un error.
        """
        self.ensure_one()
        client = Client(self.sudo().flow_api_key, self.sudo().flow_private_key,
                        self._flow_get_api_url(), False)
        try:
            response = client.make_request(method, endpoint, data=dict(data))
        except Exception as error:
            _logger.warning("Flow: error de conexión en %s: %s", endpoint, error)
            raise ValidationError(_("No se pudo conectar con Flow. Inténtalo de nuevo.")) from error
        raw = response.data.decode() if response.data else ''
        try:
            content = json.loads(raw) if raw else {}
        except ValueError:
            content = {}
        if response.status != 200 or (isinstance(content, dict) and content.get('code')
                                       and not content.get('flowOrder') and not content.get('token')):
            message = content.get('message') if isinstance(content, dict) else raw[:200]
            _logger.warning("Flow: respuesta %s en %s: %s", response.status, endpoint, raw[:500])
            raise ValidationError(_("Flow devolvió un error: %s", message or response.status))
        return content

    @api.model
    def _flow_get_payment_status(self, provider_id, token):
        """Consulta el estado de un pago en Flow a partir del token de notificación."""
        provider = self.sudo().browse(int(provider_id)).exists()
        if not provider or provider.code != 'flow':
            raise ValidationError(_("Proveedor Flow no encontrado."))
        return provider._flow_send_request('GET', '/payment/getStatus', {'token': token})
