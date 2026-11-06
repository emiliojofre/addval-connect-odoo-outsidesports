# -*- coding: utf-8 -*-
import logging

from odoo import _, models

from odoo.addons.internal_credit_payment.controllers.main import InternalCreditPayment

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        if self.provider_code != 'credit':
            return super()._get_specific_rendering_values(processing_values)
        return {
            'api_url': InternalCreditPayment._process_url,
            'reference': self.reference,
        }

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'credit':
            return super()._extract_amount_data(payment_data)
        return None  # El importe es el de la propia transacción.

    def _apply_updates(self, payment_data):
        if self.provider_code != 'credit':
            return super()._apply_updates(payment_data)
        if self.state != 'draft':
            return  # Ya procesada: no descontar dos veces.

        partner = self.partner_id._get_credit_partner()
        if not partner:
            self._set_error(_("Este cliente no tiene crédito habilitado."))
            return
        balance = partner.custom_credit
        if self.currency_id.compare_amounts(balance, self.amount) < 0 and not partner.allow_credit:
            self._set_error(_(
                "Saldo de crédito insuficiente (disponible: %(balance)s). "
                "Vuelva al pago y elija otro método.",
                balance=self.currency_id.format(balance),
            ))
            return

        partner._credit_charge(self.amount)
        _logger.info(
            "Crédito interno: %s descontado a %s por %s", self.amount, partner.display_name, self.reference)
        self._set_pending()
        # Como en 16: el pedido queda confirmado y la transacción pendiente.
        orders = self.sale_order_ids.filtered(lambda so: so.state in ('draft', 'sent'))
        orders.with_context(send_email=True).action_confirm()

    def _log_received_message(self):
        other = self.filtered(lambda t: t.provider_code != 'credit')
        super(PaymentTransaction, other)._log_received_message()

    def _get_sent_message(self):
        message = super()._get_sent_message()
        if self.provider_code == 'credit':
            message = _("El cliente pagó con %(provider_name)s.", provider_name=self.provider_id.name)
        return message
