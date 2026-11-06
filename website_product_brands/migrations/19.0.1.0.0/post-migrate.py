# Upgrade 16 -> 19 (Outside Sports): reactiva las vistas COW que desactivó el
# pre-migrate de website_base_filter_attribute. Las que ya no tienen vista
# genérica con la misma clave (vistas eliminadas en el port) se borran.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

PARAM = 'outside_upgrade19.cow_view_ids'
MODULE = 'website_product_brands'


def _drop_obsolete_views(env):
    """Borra las vistas del módulo que ya no están en su XML (y sus COW) antes
    de que Odoo valide las vistas del módulo (con el arch de 16 falla)."""
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


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    _drop_obsolete_views(env)
    value = env['ir.config_parameter'].sudo().get_param(PARAM) or ''
    ids = [int(x) for x in value.split(',') if x.strip().isdigit()]
    views = env['ir.ui.view'].browse(ids).exists()
    View = env['ir.ui.view']
    to_activate = View
    to_delete = View
    for view in views:
        if not view.website_id:
            to_activate |= view
            continue
        generic = View.search([('key', '=', view.key), ('website_id', '=', False)], limit=1)
        if generic:
            to_activate |= view
        else:
            to_delete |= view
    if to_delete:
        to_delete.with_context(no_cow=True, _force_unlink=True).unlink()
    if to_activate:
        to_activate.with_context(no_cow=True).write({'active': True})
    env['ir.config_parameter'].sudo().search([('key', '=', PARAM)]).unlink()
    _logger.info("upgrade19: COW reactivadas %s, borradas %s", to_activate.ids, to_delete.ids)
