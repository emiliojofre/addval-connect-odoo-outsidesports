# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): flujo estándar de proveedores de redirección
# de 19 (como payment_mercado_pago):
# - _get_specific_rendering_values crea el pago en Flow (/payment/create) y el
#   formulario de redirección envía al cliente a la URL de Flow con el token.
# - El webhook y el retorno consultan /payment/getStatus y llaman a _process(),
#   que valida importe y moneda (_extract_amount_data) y aplica el estado
#   (_apply_updates).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.urls import urljoin

_logger = logging.getLogger(__name__)

# Estados de Flow: 1 pendiente, 2 pagada, 3 rechazada, 4 anulada.
FLOW_STATUS_PENDING = (1,)
FLOW_STATUS_DONE = (2,)
FLOW_STATUS_ERROR = (3,)
FLOW_STATUS_CANCELED = (4,)
FLOW_MIN_AMOUNT = 350


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    flow_token = fields.Char(string="Flow Token Transaction", readonly=True, copy=False)
    fees = fields.Monetary(
        string="Comisión Flow", currency_field='currency_id', readonly=True, copy=False,
        help="Comisión informada por Flow para este pago.")

    def _get_specific_rendering_values(self, processing_values):
        if self.provider_code != 'flow':
            return super()._get_specific_rendering_values(processing_values)

        amount = self.currency_id.round(self.amount)
        if amount < FLOW_MIN_AMOUNT:
            raise ValidationError(_("Monto total no debe ser menor a $%s", FLOW_MIN_AMOUNT))
        provider = self.provider_id
        base_url = provider.get_base_url()
        payload = {
            'commerceOrder': self.reference,
            'subject': '%s: %s' % (self.company_id.name, self.reference),
            'currency': self.currency_id.name,
            'amount': f"{amount}",
            'email': self.partner_email or self.partner_id.email or '',
            'paymentMethod': int(provider.flow_payment_method or 9),
            # Mismas URLs que en 16, para que los pagos iniciados antes del
            # cambio de versión se sigan confirmando.
            'urlConfirmation': urljoin(base_url, '/payment/flow/notify/%s' % provider.id),
            'urlReturn': urljoin(base_url, '/payment/flow/return/%s' % provider.id),
        }
        try:
            response = provider._flow_send_request('POST', '/payment/create', payload)
        except ValidationError as error:
            self._set_error(str(error))
            return {}
        if not response.get('url') or not response.get('token'):
            self._set_error(_("Flow no devolvió la URL de pago."))
            return {}
        self.write({'flow_token': response['token'], 'provider_reference': response.get('flowOrder')})
        return {
            'api_url': response['url'],
            'flow_token': response['token'],
        }

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        if provider_code != 'flow':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('commerceOrder')

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'flow':
            return super()._extract_amount_data(payment_data)
        return {
            'amount': float(payment_data.get('amount') or 0),
            'currency_code': payment_data.get('currency'),
        }

    def _apply_updates(self, payment_data):
        if self.provider_code != 'flow':
            return super()._apply_updates(payment_data)

        values = {}
        if payment_data.get('flowOrder'):
            values['provider_reference'] = str(payment_data['flowOrder'])
        if payment_data.get('token'):
            values['flow_token'] = payment_data['token']
        fee = (payment_data.get('paymentData') or {}).get('fee')
        if fee:
            values['fees'] = float(fee)
        if values:
            self.write(values)

        try:
            status = int(payment_data.get('status'))
        except (TypeError, ValueError):
            status = None
        if status in FLOW_STATUS_DONE:
            self._set_done()
        elif status in FLOW_STATUS_PENDING:
            self._set_pending()
        elif status in FLOW_STATUS_CANCELED:
            self._set_canceled(state_message=_("Pago anulado en Flow."))
        elif status in FLOW_STATUS_ERROR:
            self._set_error(_("Pago rechazado por Flow."))
        else:
            _logger.warning("Flow: estado no reconocido %r para %s", payment_data.get('status'), self.reference)
            self._set_error(_("Flow devolvió un estado no reconocido: %s", payment_data.get('status')))

    def action_flow_fetch_status(self):
        """Botón: consulta en Flow el estado del pago por su referencia (commerceId)."""
        for tx in self.filtered(lambda t: t.provider_code == 'flow'):
            data = tx.provider_id._flow_send_request(
                'GET', '/payment/getStatusByCommerceId', {'commerceId': tx.reference})
            tx._process('flow', data)
        return True
