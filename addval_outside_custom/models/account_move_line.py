# -*- coding: utf-8 -*-
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_name(self):
        super()._compute_name()
        for line in self:
            # Solo líneas nuevas de documentos de venta: una línea ya guardada
            # no se toca, para no pisar una edición manual.
            if (line.product_id and not line._origin.id
                    and line.display_type not in ('line_section', 'line_note')
                    and line.move_id.is_sale_document(include_receipts=True)):
                product = line.product_id.with_context(display_default_code=False)
                if line.partner_id.lang:
                    product = product.with_context(lang=line.partner_id.lang)
                line.name = product.display_name
