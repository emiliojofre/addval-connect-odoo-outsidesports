# Upgrade 16 -> 19 (Outside Sports): este módulo queda vacío. Borra sus
# registros de 16 (crons, informes, acciones, vistas y copias por sitio) antes
# de que Odoo valide las vistas; con el arch de 16 esa validación falla.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'addval_sale'
MODELS = ['ir.cron', 'ir.actions.report', 'ir.actions.server', 'ir.ui.view']


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    loaded = env.registry.loaded_xmlids
    for model in MODELS:
        imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', model)])
        obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
        records = env[model].browse(obsolete.mapped('res_id')).exists()
        if model == 'ir.ui.view' and records:
            keys = [k for k in records.mapped('key') if k]
            cows = env[model].search([('key', 'in', keys), ('website_id', '!=', False)]) if keys else env[model]
            records = (records | cows).with_context(no_cow=True, _force_unlink=True)
        if records:
            _logger.info("upgrade19 %s: borrando %s %s", MODULE, model, records.ids)
            records.unlink()
        obsolete.exists().unlink()
