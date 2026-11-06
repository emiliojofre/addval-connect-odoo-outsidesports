# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): informe PDF con los mismos datos que el CSV
# del portal (ver wizard). get_report_values pasa a _get_report_values (17+).
from odoo import api, models


class ReportPricelistBasedProductDetails(models.AbstractModel):
    _name = 'report.pricelist_based_product_report.report_pricelist_products'
    _description = 'Pricelist Based Product Details Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        partner = self.env['res.partner'].browse(data.get('partner_id')) if data.get('partner_id') \
            else self.env.user.partner_id
        wizard = self.env['pricelist.based.product.report.wizard'].sudo().new({'partner_id': partner.id})
        data['products'] = wizard._get_catalog_lines(partner.sudo().property_product_pricelist)
        return data
