# Upgrade 16 -> 19 (Outside Sports): addval_accounting de Addval se sustituye por
# este módulo. Borra las vistas del módulo de 16 que ya no
# están en su XML (y sus copias por sitio) ANTES de que Odoo valide las vistas
# del módulo; con el arch de 16 esa validación falla. Es lo mismo que haría
# Odoo al final de la carga (_process_end), pero a tiempo.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'addval_accounting'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    loaded = env.registry.loaded_xmlids
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
    View = env['ir.ui.view']
    views = View.browse(obsolete.mapped('res_id')).exists()
    if views:
        keys = views.mapped('key')
        cows = View.search([('key', 'in', keys), ('website_id', '!=', False)]) if 'website_id' in View._fields else View
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s y copias %s", MODULE, keys, cows.ids)
        (cows | views).with_context(no_cow=True, _force_unlink=True).unlink()
    obsolete.exists().unlink()

    _deactivate_views_of_missing_modules(env)


def _deactivate_views_of_missing_modules(env):
    """Módulos que siguen "instalados" en la base pero cuyo código 19 no está
    (hoy addval_bank_sync / Fintoc, que actualiza su proveedor): sus vistas
    heredadas siguen activas y usan campos que no existen, y el navegador
    falla al abrir Contabilidad (tablero de diarios). Se desactivan; si el
    módulo llega con versión 19 su código está disponible y no se tocan."""
    from odoo.modules.module import get_manifest

    modules = env['ir.module.module'].search([('state', 'in', ('installed', 'to upgrade'))])
    missing = [m.name for m in modules if not get_manifest(m.name).get('installable')]
    if not missing:
        return
    # SQL directo: con el ORM, write() valida cada vista y las de modelos que
    # ya no existen (p. ej. fintoc.event) hacen fallar toda la actualización.
    env.cr.execute("""
        UPDATE ir_ui_view v SET active = FALSE
          FROM ir_model_data d
         WHERE d.model = 'ir.ui.view' AND d.res_id = v.id
           AND d.module IN %s AND v.active
     RETURNING v.id
    """, [tuple(missing)])
    ids = [r[0] for r in env.cr.fetchall()]
    env.cr.execute("""
        UPDATE ir_ui_menu m SET active = FALSE
          FROM ir_model_data d
         WHERE d.model = 'ir.ui.menu' AND d.res_id = m.id
           AND d.module IN %s AND m.active
     RETURNING m.id
    """, [tuple(missing)])
    menu_ids = [r[0] for r in env.cr.fetchall()]
    env['ir.ui.view'].invalidate_model(['active'])
    env['ir.ui.menu'].invalidate_model(['active'])
    _logger.info("upgrade19: módulos sin código %s, vistas desactivadas %s, menús %s",
                 missing, ids, menu_ids)
