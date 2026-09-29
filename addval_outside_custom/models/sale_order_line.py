# -*- coding: utf-8 -*-
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        """Al facturar, la descripción de la línea de factura es solo el nombre
        de la variante (sin código ni descripción de venta). La orden de venta
        no cambia."""
        res = super()._prepare_invoice_line(**optional_values)
        if self.product_id:
            product = self.product_id.with_context(display_default_code=False)
            if self.order_id.partner_id.lang:
                product = product.with_context(lang=self.order_id.partner_id.lang)
            res['name'] = product.display_name
        return res
