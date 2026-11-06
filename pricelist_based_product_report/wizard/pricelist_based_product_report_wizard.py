# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports). CSV "Descarga catálogo y stock" del portal.
#
# Se conserva el comportamiento de 16 (mismas columnas, productos según las
# reglas de la tarifa del cliente, primera regla que aplica gana, solo variantes
# publicadas, precios redondeados, sugerido x 1,19) y se corrigen errores:
# - La tarifa de precio sugerido se buscaba como 'Sugerido Público' y en la base
#   se llama 'Sugerido a público': la columna salía siempre en 0.
# - En reglas por producto/categoría/global/marca se calculaba el precio sobre
#   line.product_id (vacío) en vez de la variante; en 19 eso falla.
# - Categoría: se aplica a la categoría y sus hijas (como la regla de tarifa),
#   no a sus padres.
# - URL del producto: la URL real de la ficha (website_url).
import csv
import logging
from io import StringIO

from odoo import _, fields, models
from odoo.http import request

try:
    from unidecode import unidecode
except ImportError:  # pragma: no cover
    def unidecode(value):
        return value

_logger = logging.getLogger(__name__)

SUGGESTED_PRICELIST_NAMES = ('Sugerido a público', 'Sugerido Público')


class PricelistBasedProductReportWizard(models.TransientModel):
    _name = 'pricelist.based.product.report.wizard'
    _description = 'Pricelist Based Product Report'

    partner_id = fields.Many2one('res.partner', 'Customer')
    json_file = fields.Text('File')
    filename = fields.Char('Filename')
    mimetype = fields.Char('Mimetype')

    def _get_suggested_pricelist(self):
        Pricelist = self.env['product.pricelist'].sudo()
        for name in SUGGESTED_PRICELIST_NAMES:
            pricelist = Pricelist.search([('name', '=', name)], limit=1)
            if pricelist:
                return pricelist
        return Pricelist.search([('name', 'ilike', 'sugerido')], limit=1)

    def _get_rule_variants(self, item):
        Product = self.env['product.product'].sudo()
        if item.applied_on == '0_product_variant':
            variants = item.product_id
        elif item.applied_on == '1_product':
            variants = item.product_tmpl_id.product_variant_ids
        elif item.applied_on == '2_product_category':
            variants = Product.search([('categ_id', 'child_of', item.categ_id.id)]) if item.categ_id else Product
        elif item.applied_on == '3_global':
            variants = Product.search([])
        elif item.applied_on == '4_brand' and 'brand_id' in item._fields:
            variants = Product.search([('product_tmpl_id.product_brand_id', '=', item.brand_id.id)]) \
                if item.brand_id else Product
        else:
            variants = Product
        return variants.sudo().filtered('website_published')

    def _get_catalog_lines(self, pricelist):
        suggested = self._get_suggested_pricelist()
        base_url = request.httprequest.host_url.rstrip('/') if request else self.get_base_url()
        seen = set()
        lines = []
        for item in pricelist.sudo().item_ids:
            for product in self._get_rule_variants(item):
                if product.id in seen:
                    continue
                seen.add(product.id)
                customer_price = pricelist._get_product_price(product, 1) or product.lst_price
                selling_price = (suggested._get_product_price(product, 1) if suggested else 0.0) \
                    or product.lst_price
                lines.append({
                    'code': product.default_code or '',
                    'product_name': unidecode(product.name or ''),
                    'barcode': product.barcode or '',
                    'brand': product.product_tmpl_id.product_brand_id.name or '',
                    'product_url': base_url + (product.website_url or ''),
                    'principal_image_url': '%s/web/image/product.product/%s/image_1920' % (base_url, product.id),
                    'quantity': product.qty_available,
                    'customer_price': round(customer_price, 0),
                    'selling_price': round(selling_price, 0),
                })
        return sorted(lines, key=lambda line: line['product_name'])

    def generate_report_from_website(self):
        self.ensure_one()
        partner = self.partner_id or self.env.user.partner_id
        pricelist = partner.property_product_pricelist

        csvfile = StringIO()
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([
            _("Codigo"), _("Descripcion"), _("Codigo EAN"), _("Marca"), _("URL Producto"),
            _("URL imagen"), _("Stock disponible"), _("Precio de venta"), _("Precio sugerido a publico"),
        ])
        for line in self._get_catalog_lines(pricelist):
            writer.writerow([
                line['code'],
                line['product_name'],
                line['barcode'],
                line['brand'],
                line['product_url'],
                line['principal_image_url'],
                str(int(line['quantity'])),
                str(line['customer_price']),
                str(int(line['selling_price']) * 1.19),
            ])
        self.write({
            'json_file': csvfile.getvalue(),
            'filename': 'Pricelist Based Product.csv',
            'mimetype': 'text/csv',
        })
        csvfile.close()
        return self

    def generate_report(self):
        """Botón del asistente de backend: genera el CSV del cliente elegido y lo descarga."""
        self.generate_report_from_website()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=json_file&filename_field=filename&download=true'
                   % (self._name, self.id),
            'target': 'self',
        }
