# -*- coding: utf-8 -*-
from odoo import fields, models


class PartnerCredit(models.Model):
    _name = 'partner.credit'
    _description = 'Crédito de cliente'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Cliente', index=True)
    credit = fields.Float('Crédito', readonly=True)
    # Nombre heredado de 16 (se conserva para no perder datos).
    update = fields.Float('Actualizar')

    _unique_partner_value = models.Constraint(
        'unique(partner_id)', 'Cada cliente solo puede tener un registro de crédito.',
    )

    def do_update(self):
        """Suma "Actualizar" al saldo del cliente y lo deja en el historial
        (mismo comportamiento que en 16)."""
        History = self.env['update.credit.history'].sudo()
        for rec in self:
            partner = rec.partner_id
            if rec.update > 0.0:
                total = rec.update + rec.credit
                History.create({
                    'approve_date': fields.Date.context_today(rec),
                    'updated_amount': rec.update,
                    'prev_amount': partner.custom_credit if partner.update_credit_ids else 0.0,
                    'amount': total,
                    'partner_id': partner.id,
                })
                rec.credit = total
                partner.custom_credit = total
            if partner.custom_credit != 0.0:
                rec.credit = partner.custom_credit
            rec.update = 0.0


class UpdateCreditHistory(models.Model):
    _name = 'update.credit.history'
    _description = 'Historial de crédito'
    _order = 'approve_date desc, id desc'

    approve_date = fields.Date('Fecha')
    updated_amount = fields.Float('Movimiento')
    prev_amount = fields.Float('Saldo anterior')
    amount = fields.Float('Saldo')
    partner_id = fields.Many2one('res.partner', string='Cliente', index=True)


class UpdateCreditHistoryPayment(models.Model):
    _name = 'update.credit.history.payment'
    _description = 'Historial de crédito con pago'
    _order = 'approve_date desc, id desc'

    approve_date = fields.Date('Fecha')
    updated_amount = fields.Float('Movimiento')
    prev_amount = fields.Float('Saldo anterior')
    payment_refer = fields.Many2one('account.payment', string='Pago')
    amount = fields.Float('Saldo')
    partner_id = fields.Many2one('res.partner', string='Cliente', index=True)
