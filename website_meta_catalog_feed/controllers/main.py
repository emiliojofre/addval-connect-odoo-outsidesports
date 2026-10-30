import logging
import re
import time

from lxml import etree

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

PARAM_WEBSITE_IDS = 'website_meta_catalog_feed.website_ids'
G_NS = 'http://base.google.com/ns/1.0'
CACHE_SECONDS = 3600

# {website_id: (timestamp, xml_bytes)}. Cache por worker: Meta lee el feed
# una vez al día, esto solo evita recalcular 1.000+ precios si alguien lo
# recarga seguido.
_feed_cache = {}


class MetaCatalogFeed(http.Controller):

    @http.route('/meta-catalog.xml', type='http', auth='public', website=True,
                sitemap=False, multilang=False)
    def meta_catalog_feed(self, **kwargs):
        website = request.website
        allowed = request.env['ir.config_parameter'].sudo().get_param(PARAM_WEBSITE_IDS, '3')
        if str(website.id) not in [w.strip() for w in allowed.split(',')]:
            raise request.not_found()

        cached = _feed_cache.get(website.id)
        if cached and time.time() - cached[0] < CACHE_SECONDS and not kwargs.get('nocache'):
            body = cached[1]
        else:
            started = time.time()
            body = self._build_feed(website)
            _feed_cache[website.id] = (time.time(), body)
            _logger.info("Meta catalog feed sitio %s generado en %.1fs",
                         website.id, time.time() - started)

        return request.make_response(body, headers=[
            ('Content-Type', 'application/xml; charset=utf-8'),
            ('Cache-Control', 'public, max-age=%d' % CACHE_SECONDS),
        ])

    def _build_feed(self, website):
        env = request.env(context=dict(
            request.env.context,
            website_id=website.id,
            lang=website.default_lang_id.code or request.env.context.get('lang'),
        ))
        website = website.with_env(env)
        base_url = website.get_base_url()
        pricelist = website.pricelist_id
        currency = pricelist.currency_id or website.currency_id

        templates = env['product.template'].search(
            website.sale_product_domain() + [('is_published', '=', True)])

        rss = etree.Element('rss', version='2.0', nsmap={'g': G_NS})
        channel = etree.SubElement(rss, 'channel')
        etree.SubElement(channel, 'title').text = website.name
        etree.SubElement(channel, 'link').text = base_url
        etree.SubElement(channel, 'description').text = 'Catálogo %s' % website.name

        for template in templates:
            for variant in template.product_variant_ids:
                try:
                    item = self._feed_item(template, variant, website, pricelist,
                                           currency, base_url)
                except Exception:
                    _logger.exception("Meta catalog feed: se omite la variante %s",
                                      variant.id)
                    continue
                if item is not None:
                    channel.append(item)

        return etree.tostring(rss, xml_declaration=True, encoding='utf-8')

    def _feed_item(self, template, variant, website, pricelist, currency, base_url):
        # Con website_id=3 en el contexto, addval_website_chile devuelve los
        # precios con IVA incluido, igual que la ficha del B2C.
        info = template._get_combination_info(
            product_id=variant.id, pricelist=pricelist)
        price = info.get('price') or 0.0
        list_price = info.get('list_price') or price
        if price <= 0:
            # Meta rechaza productos sin precio.
            return None

        # Misma regla de disponibilidad que el JSON-LD de la ficha (vista 5811).
        stock_variant = variant.sudo()
        if stock_variant.detailed_type != 'product' or stock_variant.free_qty > 0:
            availability = 'in stock'
        elif template.allow_out_of_stock_order:
            availability = 'available for order'
        else:
            availability = 'out of stock'

        title = template.name
        attributes = variant.product_template_attribute_value_ids._get_combination_name()
        if attributes:
            title = '%s (%s)' % (title, attributes)

        description = (template.website_meta_description or template.description_sale
                       or template.name)

        item = etree.Element('item')

        def add(tag, value):
            if value:
                etree.SubElement(item, '{%s}%s' % (G_NS, tag)).text = str(value)

        add('id', variant.default_code or 'variant-%s' % variant.id)
        if template.product_variant_count > 1:
            add('item_group_id', 'template-%s' % template.id)
        add('title', title[:200])
        add('description', description.strip()[:9999])
        # website_url de la variante ya trae #attr=..., así la ficha abre con
        # esa talla/color seleccionada.
        add('link', base_url + variant.website_url)
        add('image_link', base_url + website.image_url(variant, 'image_1024'))
        add('availability', availability)
        add('condition', 'new')
        add('price', self._format_price(max(list_price, price), currency))
        if list_price > price:
            add('sale_price', self._format_price(price, currency))
        add('brand', template.product_brand_id.name or website.company_id.name)
        if variant.barcode and re.fullmatch(r'\d{8,14}', variant.barcode):
            add('gtin', variant.barcode)
        category = template.public_categ_ids[:1]
        if category:
            add('product_type', ' > '.join(category.parents_and_self.mapped('name')))
        return item

    @staticmethod
    def _format_price(amount, currency):
        amount = currency.round(amount)
        if currency.decimal_places:
            return '%.*f %s' % (currency.decimal_places, amount, currency.name)
        return '%d %s' % (round(amount), currency.name)
