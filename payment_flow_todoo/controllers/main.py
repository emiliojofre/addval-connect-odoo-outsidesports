# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): webhook y retorno de Flow con el flujo
# estándar _process(). Se mantienen las URLs de 16.
import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class FlowController(http.Controller):

    def _flow_process(self, provider_id, token):
        data = request.env['payment.provider'].sudo()._flow_get_payment_status(provider_id, token)
        _logger.info("Flow: estado recibido:\n%s", pprint.pformat(data))
        return request.env['payment.transaction'].sudo()._process('flow', data)

    @http.route([
        '/payment/flow/notify/<string:provider_id>',
    ], type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def flow_webhook(self, provider_id, **post):
        """Notificación servidor a servidor de Flow (urlConfirmation)."""
        token = post.get('token')
        if not token:
            return request.make_response('', status=400)
        try:
            self._flow_process(provider_id, token)
        except ValidationError:
            _logger.exception("Flow: no se pudo procesar la notificación")
        return ''

    @http.route([
        '/payment/flow/return/<string:provider_id>',
    ], type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def flow_return(self, provider_id, **post):
        """Vuelta del cliente desde Flow (urlReturn)."""
        token = post.get('token')
        if token:
            try:
                self._flow_process(provider_id, token)
            except ValidationError:
                _logger.exception("Flow: no se pudo procesar el retorno")
        return request.redirect('/payment/status')
