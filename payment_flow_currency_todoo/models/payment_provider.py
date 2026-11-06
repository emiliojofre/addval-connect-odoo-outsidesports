# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): se conservan los campos (en producción
# vacíos/desactivados). compute_fees se elimina: la función de comisiones ya
# no existe en el núcleo desde 17. Para limitar monedas, 19 tiene el campo
# estándar available_currency_ids en el proveedor.
from odoo import models, fields


class PaymentAcquirerCurrency(models.Model):
    _inherit = 'payment.provider'

    currency_ids = fields.Many2many(
        'res.currency',
        string='Currencies',
        help="Use only these allowed currencies."
    )
    force_currency = fields.Boolean(
        string="Force Currency",
    )
    force_currency_id = fields.Many2one(
        'res.currency',
        string='Currency id',
    )
