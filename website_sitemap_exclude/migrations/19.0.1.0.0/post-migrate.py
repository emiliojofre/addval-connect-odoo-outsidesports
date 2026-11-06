# Upgrade 16 -> 19 (Outside Sports): adapta las vistas SEO "outside_seo.*".
# Son vistas creadas directamente en la base (sin módulo ni xmlid), así que
# ningún módulo las actualiza; se reescriben aquí con las estructuras de 19.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# /shop y /shop/category: H1 con el título SEO de la categoría y descripción de
# la categoría debajo del paginador (en 19 el H1 y la descripción ya están en
# la cabecera estándar, así que se reemplaza el texto y se mueve el bloque).
CATEGORY_TEXT = """<data>
  <xpath expr="//h1[contains(@t-attf-class, 'o_wsale_category_title')]//t[@t-elif='category']/span" position="replace">
    <span t-out="(category.website_meta_title or category.name).split(' | ')[0]"/>
  </xpath>
  <xpath expr="//div[@id='category_header']" position="replace"/>
  <xpath expr="//div[@id='o_wsale_pager']" position="after">
    <t t-if="category">
      <t t-set="editor_msg">Arrastre bloques aquí para agregar texto a la categoría "<t t-out="category.name"/>".</t>
      <div class="mt-4 mb16" id="category_header" t-att-data-editor-message="editor_msg" t-field="category.website_description"/>
    </t>
  </xpath>
</data>"""

# Ficha: en 19 el precio ya no lleva microdatos ni el precio neto oculto fuera
# del modo edición; solo se añade la etiqueta "IVA incluido".
PRODUCT_PRICE = """<data>
  <xpath expr="//div[@name='product_price_container']/span[hasclass('oe_price')]" position="attributes">
    <attribute name="data-iva-label-added">1</attribute>
  </xpath>
  <xpath expr="//div[@name='product_price_container']/span[hasclass('oe_price')]" position="after">
    <small class="text-muted ms-2">IVA incluido</small>
  </xpath>
</data>"""

# JSON-LD de la ficha: detailed_type ya no existe en 19 (is_storable).
JSONLD_REPLACE = (
    "ld_pv.detailed_type != 'product'",
    "not ld_pv.is_storable",
)

# Depende de la etiqueta "+ IVA" de addval_website_chile (aún no portado):
# se desactiva hasta portar ese módulo.
DEACTIVATE = ['outside_seo.product_listing_price_label']


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    View = env['ir.ui.view'].with_context(no_cow=True)

    views = View.search([('key', '=', 'outside_seo.category_text_below_products')])
    views.write({'arch': CATEGORY_TEXT})
    _logger.info("upgrade19 outside_seo: category_text_below_products %s", views.ids)

    views = View.search([('key', '=', 'outside_seo.product_price_no_microdata')])
    views.write({'arch': PRODUCT_PRICE})
    _logger.info("upgrade19 outside_seo: product_price_no_microdata %s", views.ids)

    for view in View.search([('key', '=', 'outside_seo.product_jsonld')]):
        if JSONLD_REPLACE[0] in view.arch:
            view.write({'arch': view.arch.replace(*JSONLD_REPLACE)})
            _logger.info("upgrade19 outside_seo: product_jsonld %s", view.id)

    views = View.search([('key', 'in', DEACTIVATE), ('active', '=', True)])
    views.write({'active': False})
    _logger.info("upgrade19 outside_seo: desactivadas %s", views.ids)
