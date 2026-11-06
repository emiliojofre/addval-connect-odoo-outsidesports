from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_product_pvp = fields.Monetary(
        'PVP', default=1,currency_field='currency_id', compute='_compute_product_pvp'
    )


    @api.depends('lst_price')
    def _compute_product_pvp(self):
        for record in self:
            record.product_product_pvp = record.lst_price * 1.19