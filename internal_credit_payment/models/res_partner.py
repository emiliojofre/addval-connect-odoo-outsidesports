# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    update_credit_ids = fields.One2many('update.credit.history', 'partner_id', string='Historial de crédito')
    update_credit_payment_ids = fields.One2many(
        'update.credit.history.payment', 'partner_id', string='Historial de crédito con pago')
    custom_credit = fields.Float('Crédito')
    allow_credit = fields.Boolean(
        'Permitir pagar con crédito aunque el pedido supere el saldo', default=False)

    def _get_credit_partner(self):
        """Contacto que lleva el crédito: el propio o, si no tiene registro de
        crédito, su empresa. Vacío si ninguno lo tiene."""
        self.ensure_one()
        Credit = self.env['partner.credit'].sudo()
        for partner in (self, self.commercial_partner_id):
            if Credit.search_count([('partner_id', '=', partner.id)], limit=1):
                return partner
        return self.browse()

    def action_view_credit_detail(self):
        self.ensure_one()
        credits = self.env['partner.credit'].sudo().search([('partner_id', '=', self.id)])
        credits.do_update()
        return {
            'name': 'Crédito',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'partner.credit',
            'domain': [('partner_id', '=', self.id)],
        }

    def _credit_charge(self, amount):
        """Descuenta `amount` del saldo y lo registra en el historial (lo que
        hacía /shop/payment/validate en 16). Devuelve el saldo nuevo."""
        self.ensure_one()
        partner = self.sudo()
        balance = partner.custom_credit
        new_balance = balance - amount
        partner.custom_credit = new_balance
        Credit = self.env['partner.credit'].sudo()
        credit = Credit.search([('partner_id', '=', partner.id)], limit=1)
        if credit:
            credit.do_update()
        else:
            Credit.create({'partner_id': partner.id, 'credit': new_balance})
        self.env['update.credit.history'].sudo().create({
            'approve_date': fields.Date.context_today(self),
            'updated_amount': -amount,
            'prev_amount': balance,
            'amount': new_balance,
            'partner_id': partner.id,
        })
        return new_balance
