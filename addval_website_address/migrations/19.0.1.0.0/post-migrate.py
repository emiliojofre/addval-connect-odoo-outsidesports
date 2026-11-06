# Upgrade 16 -> 19 (Outside Sports): borra las vistas de este módulo que ya no
# están en su XML ANTES de que Odoo valide las vistas del módulo (con el arch
# de 16 la validación y el render fallan).
# Además de las vistas con xmlid obsoleto y sus copias por sitio, se borran las
# vistas con clave "addval_website_address.*" sin xmlid: el hook de
# addval_website_chile (16) reapuntó el xmlid de address_custom y dejó copias
# huérfanas, incluso genéricas (sin website_id).
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'addval_website_address'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    loaded = env.registry.loaded_xmlids
    View = env['ir.ui.view']
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    keep_ids = set(imds.filtered(lambda d: '%s.%s' % (d.module, d.name) in loaded).mapped('res_id'))
    views = View.search([('key', '=like', MODULE + '.%')])
    obsolete_keys = set((View.browse(imds.mapped('res_id')).exists() - View.browse(list(keep_ids))).mapped('key'))
    kept_keys = set(View.browse(list(keep_ids)).exists().mapped('key'))
    to_delete = views.filtered(
        lambda v: v.id not in keep_ids and (v.key in obsolete_keys or v.key not in kept_keys or not v.model_data_id)
    )
    # Nunca borrar copias por sitio de vistas vigentes que el usuario haya editado.
    to_delete = to_delete.filtered(lambda v: not (v.key in kept_keys and v.website_id and v.arch_updated))
    if to_delete:
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s", MODULE, [(v.id, v.key, v.website_id.id) for v in to_delete])
        to_delete.with_context(no_cow=True, _force_unlink=True).unlink()
    imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded).exists().unlink()
