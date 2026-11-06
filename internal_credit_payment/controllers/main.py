# -*- coding: utf-8 -*-
import logging
import pprint

from odoo.http import Controller, request, route

_logger = logging.getLogger(__name__)


class InternalCreditPayment(Controller):
    # Misma URL que en 16.
    _process_url = '/credit/payment/feedback'

    @route(_process_url, type='http', auth='public', methods=['POST'], csrf=False)
    def credit_process_transaction(self, **post):
        _logger.info("Pago con crédito interno, datos:\n%s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._process('credit', post)
        return request.redirect('/payment/status')
