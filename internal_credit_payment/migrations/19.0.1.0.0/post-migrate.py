# Upgrade 16 -> 19 (Outside Sports):
# * borra las vistas de 16 que ya no están en el XML (y sus copias por sitio)
#   antes de que Odoo valide las vistas del módulo;
# * completa el proveedor "credit" (noupdate) con el formulario de redirección
#   y el método de pago que exige 19;
# * borra los menús web "/credit" (la página ya no existe).
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'internal_credit_payment'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})

    loaded = env.registry.loaded_xmlids
    imds = env['ir.model.data'].search([('module', '=', MODULE), ('model', '=', 'ir.ui.view')])
    obsolete = imds.filtered(lambda d: '%s.%s' % (d.module, d.name) not in loaded)
    View = env['ir.ui.view']
    views = View.browse(obsolete.mapped('res_id')).exists()
    if views:
        keys = [k for k in views.mapped('key') if k]
        cows = View.search([('key', 'in', keys), ('website_id', '!=', False)]) if keys else View
        _logger.info("upgrade19 %s: borrando vistas obsoletas %s y copias %s", MODULE, views.ids, cows.ids)
        (cows | views).with_context(no_cow=True, _force_unlink=True).unlink()
    obsolete.exists().unlink()

    method = env.ref('internal_credit_payment.payment_method_credit')
    form = env.ref('internal_credit_payment.redirect_form')
    providers = env['payment.provider'].search([('code', '=', 'credit')])
    providers.write({
        'redirect_form_view_id': form.id,
        'payment_method_ids': [(6, 0, method.ids)],
    })
    _logger.info("upgrade19 %s: proveedores %s con método %s", MODULE, providers.ids, method.id)

    menus = env['website.menu'].search([('url', 'in', ('/credit', '/add/credit/balance'))])
    if menus:
        _logger.info("upgrade19 %s: borrando menús web %s", MODULE, menus.ids)
        env['ir.model.data'].search([('model', '=', 'website.menu'), ('res_id', 'in', menus.ids)]).unlink()
        menus.unlink()
