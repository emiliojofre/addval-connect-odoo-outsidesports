# -*- coding: utf-8 -*-
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_name(self):
        super()._compute_name()
        for line in self:
            # Solo para lineas nuevas (todavia no guardadas) con producto:
            # dejar como descripcion unicamente el nombre del producto,
            # sin la descripcion de venta/compra larga. No se toca una
            # linea ya guardada para no pisar una edicion manual existente.
            if line.product_id and not line._origin.id and \
                    line.display_type not in ('line_section', 'line_note'):
                product = line.product_id
                if line.partner_id.lang:
                    product = product.with_context(lang=line.partner_id.lang)
                line.name = product.name
