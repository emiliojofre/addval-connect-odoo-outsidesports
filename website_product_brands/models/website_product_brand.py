# -*- coding: utf-8 -*-
#################################################################################
#
#	Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
# Port a Odoo 19 (Outside Sports):
# - sale_product_domain devuelve un Domain: se combina con Domain.AND.
# - El filtro de marca se lee del parámetro attrib_brand de la petición actual
#   (valores "id-id", como en 16), solo si hay petición HTTP.
# - Se elimina website_style_ids (el modelo product.style ya no existe).
from odoo import api, fields, models
from odoo.fields import Domain
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def get_wk_brands(self, brand_set):
        return self.env['wk.product.brand'].sudo().browse(list(set(brand_set)))

    def get_filter_brand(self, wk_brands):
        return ','.join(map(str, wk_brands.ids))

    @api.model
    def _get_wk_brand_set(self):
        if not request or not getattr(request, 'httprequest', None):
            return []
        brand_set = []
        for value in request.httprequest.args.getlist('attrib_brand'):
            try:
                brand_set.append(int(value.split('-')[0]))
            except (ValueError, IndexError):
                continue
        return list(set(brand_set))

    def _get_brand_domain(self):
        brand_set = self._get_wk_brand_set()
        if brand_set:
            return [('product_brand_id', 'in', brand_set)]
        return []

    def sale_product_domain(self):
        domain = super().sale_product_domain()
        brand_domain = self._get_brand_domain()
        if brand_domain:
            domain = Domain.AND([domain, brand_domain])
        return domain


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        string='Brand',
        comodel_name="wk.product.brand",
        index=True,
    )


class WkProductBrand(models.Model):
    _name = "wk.product.brand"
    _inherit = ['website.published.mixin']
    _description = "Website Product Brand"
    _order = "sequence asc"

    @api.depends('products')
    def _get_product_count(self):
        for rec in self:
            rec.total_products = len(rec.products.ids)

    name = fields.Char(string="Brand Name", required=True, translate=True)
    image = fields.Binary(
        string='product  image',
        help=" This Image will be visible to user in there shop  by brand onwebsite view !")
    description = fields.Text(string="Brand Description", translate=True)
    sequence = fields.Integer(
        string="Sequence",
        help="Gives the sequence order when displaying a list of brand onwebsite view.!")
    products = fields.One2many('product.template', 'product_brand_id')
    total_products = fields.Integer(string="Total no. of Products", compute=_get_product_count)

    website_ribbon_id = fields.Many2one('product.ribbon', string='Ribbon')
    brand_banner = fields.Binary(string="Brand Banner")
    website_id = fields.Many2one('website', string="Website", ondelete='restrict')
    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)

    country_of_origin = fields.Char(string="Country of Origin")

    def _compute_website_url(self):
        super()._compute_website_url()
        for brand in self:
            if brand.id:
                brand.website_url = '/shop?attrib_brand=%s-%s' % (brand.id, brand.id)

    @api.model
    def wk_activate_website_view(self):
        # En 19 ya no existe website_sale.products_description; solo se activa
        # el filtro de atributos (contenedor de los filtros de marca).
        products_attributes = self.env.ref('website_sale.products_attributes', raise_if_not_found=False)
        if products_attributes:
            products_attributes.write({'active': True})
        return True

    def _get_website_ribbon(self):
        return self.website_ribbon_id
