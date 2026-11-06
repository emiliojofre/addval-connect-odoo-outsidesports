# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('partner_id')
    def _compute_account_id(self):
        """En facturas de proveedor, las líneas de producto usan la
        "Cuenta Activo o Gasto" del proveedor cuando está definida.

        En 16 (Addval) la regla se aplicaba también a facturas de cliente;
        aquí solo a compras.
        """
        super()._compute_account_id()
        for line in self:
            move = line.move_id
            if line.display_type != 'product' or not move.is_purchase_document(include_receipts=True):
                continue
            partner = (line.partner_id or move.partner_id).commercial_partner_id
            if not partner:
                continue
            account = partner.with_company(line.company_id).property_account_assets_or_expenses_id
            if not account:
                continue
            if move.fiscal_position_id:
                account = move.fiscal_position_id.map_account(account)
            line.account_id = account
