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


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    _drop_obsolete_views(env)
    _set_tax_display(env)
