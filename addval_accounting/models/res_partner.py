# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Mismo nombre que en addval_accounting (16): el upgrade de Odoo conserva
    # los valores (columna jsonb por compañía).
    property_account_assets_or_expenses_id = fields.Many2one(
        'account.account',
        string='Cuenta Activo o Gasto',
        company_dependent=True,
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'off_balance'))]",
        help='Si se indica, las líneas de las facturas de proveedor de este contacto '
             'usan esta cuenta en lugar de la del producto.',
    )
