# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports):
# - En 19 el formulario de reglas usa display_applied_on ("Aplicar a") y deja
#   applied_on oculto; se añade "Marca" a ambos y se mantiene applied_on='4_brand'
#   en los onchange estándar, que si no lo pasarían a '3_global'.
# - _compute_name_and_price ya no existe: el nombre se calcula en _compute_name.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection_add=[('4_brand', "Marca")],
        ondelete={'4_brand': 'set default'})
    display_applied_on = fields.Selection(
        selection_add=[('4_brand', "Marca")],
        ondelete={'4_brand': 'set default'})

    brand_id = fields.Many2one(
        comodel_name='wk.product.brand',
        string="Marca",
        index=True)

    @api.depends('brand_id')
    def _compute_name(self):
        super()._compute_name()
        for item in self:
            if item.brand_id and item.applied_on == '4_brand':
                item.name = _("Marca: %s", item.brand_id.name)

    @api.constrains('applied_on', 'brand_id')
    def _check_brand_consistency(self):
        for item in self:
            if item.applied_on == "4_brand" and not item.brand_id:
                raise ValidationError(_("Please specify the brand for which this rule should be applied"))

    def _is_applicable_for(self, product, qty_in_product_uom):
        self.ensure_one()
        if self.applied_on == '4_brand':
            if self.min_quantity and qty_in_product_uom < self.min_quantity:
                return False
            template = product if product._name == 'product.template' else product.product_tmpl_id
            return template.product_brand_id == self.brand_id
        return super()._is_applicable_for(product, qty_in_product_uom)

    @api.onchange('display_applied_on')
    def _onchange_display_applied_on(self):
        super()._onchange_display_applied_on()
        for item in self:
            if item.display_applied_on == '4_brand':
                item.update({
                    'applied_on': '4_brand',
                    'product_id': None,
                    'product_tmpl_id': None,
                    'categ_id': None,
                })
            elif item.applied_on == '4_brand':
                item.brand_id = False

    @api.onchange('product_id', 'product_tmpl_id', 'categ_id')
    def _onchange_rule_content(self):
        super()._onchange_rule_content()
        for item in self:
            if item.display_applied_on == '4_brand':
                item.applied_on = '4_brand'

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        for item in self.filtered('brand_id'):
            item.update({'applied_on': '4_brand', 'display_applied_on': '4_brand'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('applied_on') == '4_brand' or (
                    vals.get('brand_id') and vals.get('display_applied_on') == '4_brand'):
                vals.update({
                    'applied_on': '4_brand',
                    'display_applied_on': '4_brand',
                    'product_id': None,
                    'product_tmpl_id': None,
                    'categ_id': None,
                })
        return super().create(vals_list)
