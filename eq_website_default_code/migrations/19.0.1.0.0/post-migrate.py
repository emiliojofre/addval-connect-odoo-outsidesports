# Upgrade 16 -> 19 (Outside Sports): borra las vistas de este módulo que ya no
# están en su XML (y sus copias por sitio) ANTES de que Odoo valide las vistas
# del módulo; con el arch de 16 esa validación falla. Es lo mismo que haría
# Odoo al final de la carga (_process_end), pero a tiempo.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'eq_website_default_code'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    loaded = env.registry.loaded_xmlids
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
    View = env['ir.ui.view']
    views = View.browse(obsolete.mapped('res_id')).exists()
    if views:
        keys = views.mapped('key')
        cows = View.search([('key', 'in', keys), ('website_id', '!=', False)])
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s y copias %s", MODULE, keys, cows.ids)
        (cows | views).with_context(no_cow=True, _force_unlink=True).unlink()
    obsolete.exists().unlink()
