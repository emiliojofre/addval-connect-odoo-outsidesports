# Upgrade 16 -> 19 (Outside Sports):
# 1) Borra las vistas del módulo que ya no están en su XML (y sus copias por
#    sitio) antes de que Odoo valide las vistas del módulo.
# 2) En 19 mostrar precios con o sin IVA es un ajuste por sitio: el B2C (id 3)
#    con IVA incluido y los demás sin IVA, como hacía este módulo en 16.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'addval_website_chile'
B2C_WEBSITE_ID = 3


def _drop_obsolete_views(env):
    loaded = env.registry.loaded_xmlids
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
    View = env['ir.ui.view']
    views = View.browse(obsolete.mapped('res_id')).exists()
    if views:
        keys = [k for k in views.mapped('key') if k != 'auth_signup.signup']
        cows = View.search([('key', 'in', keys), ('website_id', '!=', False)])
        cows -= views
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s y copias %s", MODULE, views.ids, cows.ids)
        (cows | views).with_context(no_cow=True, _force_unlink=True).unlink()
    obsolete.exists().unlink()


def _set_tax_display(env):
    for website in env['website'].search([]):
        value = 'tax_included' if website.id == B2C_WEBSITE_ID else 'tax_excluded'
        if website.show_line_subtotals_tax_selection != value:
            website.show_line_subtotals_tax_selection = value
            _logger.info("upgrade19 %s: sitio %s -> %s", MODULE, website.id, value)


def _set_signup_scope(env):
    """Registro libre solo en el B2C; en los demás sitios, por invitación.
    En 16 se conseguía editando a mano auth_signup.signup (vista genérica),
    pero el upgrade de Odoo restablece esa vista."""
    for website in env['website'].search([]):
        value = 'b2c' if website.id == B2C_WEBSITE_ID else 'b2b'
        if website.auth_signup_uninvited != value:
            website.auth_signup_uninvited = value
            _logger.info("upgrade19 %s: registro sitio %s -> %s", MODULE, website.id, value)


TAX_INDICATION_B2B = """<t t-name="website_sale.tax_indication">
        <span t-if="website.show_line_subtotals_tax_selection == 'tax_excluded'" class="fs-6 fw-normal text-muted text-nowrap">+ IVA</span>
        <span t-else="" class="fs-6 fw-normal text-muted text-nowrap">IVA incluido</span>
    </t>"""


def _set_b2b_tax_indication(env):
    """La copia B2B de website_sale.tax_indication viene de 16 con la etiqueta
    vacía (un carácter invisible): en el editor web de 19 el texto que se
    escribe junto al precio cae dentro del campo "Precio de venta" y el editor
    intenta guardar "$ 151.008 + IVA" como precio (error de validación).
    Se reescribe con la estructura de 19 y el texto "+ IVA" de 16."""
    views = env['ir.ui.view'].search([
        ('key', '=', 'website_sale.tax_indication'),
        ('website_id', '!=', False),
        ('website_id', '!=', B2C_WEBSITE_ID),
    ])
    for view in views:
        view.with_context(no_cow=True).write({'arch': TAX_INDICATION_B2B})
    _logger.info("upgrade19 %s: etiqueta de impuestos '+ IVA' en %s", MODULE, views.ids)


def _disable_base_unit_price(env):
    """En 19 el "Precio de referencia por unidad" (website_sale.group_show_uom_price)
    se muestra en todas las fichas de producto ("$ 217.588 / Unidad(es)").
    Outside Sports no lo usa: se desactiva como lo hace Ajustes > Sitio web."""
    implied = env.ref('website_sale.group_show_uom_price', raise_if_not_found=False)
    if not implied:
        return
    groups = env.ref('base.group_user') | env.ref('base.group_portal') | env.ref('base.group_public')
    groups.sudo()._remove_group(implied)
    implied.sudo().write({'user_ids': [(5, 0, 0)]})
    _logger.info("upgrade19 %s: precio por unidad de referencia desactivado", MODULE)


HIDDEN_HEADER_VIEWS = ['website.header_text_element', 'website.header_call_to_action']
HEADER_WEBSITE_IDS = [2, B2C_WEBSITE_ID]  # B2B y B2C


def _hide_header_phone_and_cta(env):
    """Oculta en el encabezado el teléfono (bloque de texto) y el botón
    "Contáctenos" en B2B y B2C, igual que las opciones "Visuales: T" y
    "Acciones: llamada a la acción" del editor (vistas por sitio)."""
    View = env['ir.ui.view']
    for website_id in HEADER_WEBSITE_IDS:
        for key in HIDDEN_HEADER_VIEWS:
            view = View.search([('key', '=', key), ('website_id', '=', website_id)], limit=1)
            if not view:
                generic = View.search([('key', '=', key), ('website_id', '=', False)], limit=1)
                if not generic:
                    continue
                # Escribir con website_id en el contexto crea la copia del sitio.
                generic.with_context(website_id=website_id).write({'active': False})
            elif view.active:
                view.write({'active': False})
    _logger.info("upgrade19 %s: teléfono y Contáctenos ocultos en el encabezado de %s",
                 MODULE, HEADER_WEBSITE_IDS)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    _drop_obsolete_views(env)
    _set_tax_display(env)
    _set_signup_scope(env)
    _set_b2b_tax_indication(env)
    _disable_base_unit_price(env)
    _hide_header_phone_and_cta(env)
