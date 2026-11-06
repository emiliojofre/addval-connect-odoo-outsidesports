# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('credit', 'Crédito interno')], ondelete={'credit': 'set default'})

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'credit':
            return super()._get_default_payment_method_codes()
        return {'credit'}

    @api.model
    def _get_compatible_providers(self, company_id, partner_id, amount, *args, **kwargs):
        """El crédito solo se ofrece a clientes con registro de crédito
        (cambio de Addval en 16)."""
        providers = super()._get_compatible_providers(company_id, partner_id, amount, *args, **kwargs)
        if 'credit' in providers.mapped('code'):
            partner = self.env['res.partner'].sudo().browse(partner_id).exists()
            if not partner or not partner._get_credit_partner():
                providers = providers.filtered(lambda p: p.code != 'credit')
        return providers
