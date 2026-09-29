# -*- coding: utf-8 -*-
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        """Al facturar, usar solo el nombre del producto como descripción
        de la línea de factura, en vez de la descripción de venta completa
        (que puede ser muy larga y ocupa demasiado espacio en la factura).

        Esto NO afecta la descripción que se ve en la Orden de Venta/
        Cotización, solo lo que queda escrito en la factura resultante.
        """
        res = super()._prepare_invoice_line(**optional_values)
        if self.product_id:
            product = self.product_id
            if self.order_id.partner_id.lang:
                product = product.with_context(lang=self.order_id.partner_id.lang)
            res['name'] = product.name
        return res
