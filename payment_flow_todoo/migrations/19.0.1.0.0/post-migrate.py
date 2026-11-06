# Upgrade 16 -> 19 (Outside Sports): el registro del proveedor Flow es
# noupdate, así que se completa aquí con lo que exige 19: formulario de
# redirección nuevo y el método de pago "Flow". Además se borran las vistas
# obsoletas del módulo antes de que Odoo las valide.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'payment_flow_todoo'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})

    loaded = env.registry.loaded_xmlids
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
    views = env['ir.ui.view'].browse(obsolete.mapped('res_id')).exists()
    if views:
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s", MODULE, views.mapped('key'))
        views.unlink()
    obsolete.exists().unlink()

    method = env.ref('payment_flow_todoo.payment_method_flow')
    form = env.ref('payment_flow_todoo.redirect_form')
    providers = env['payment.provider'].search([('code', '=', 'flow')])
    for provider in providers:
        provider.write({
            'redirect_form_view_id': form.id,
            'payment_method_ids': [(6, 0, method.ids)],
        })
    _logger.info("upgrade19 %s: proveedores Flow %s con método %s", MODULE, providers.ids, method.id)
