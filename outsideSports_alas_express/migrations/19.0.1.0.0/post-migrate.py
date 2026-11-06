# Upgrade 16 -> 19 (Outside Sports):
# 1) El servicio de upgrade de Odoo archiva los métodos de envío cuyo
#    delivery_type viene de un módulo que no conoce (alas_express). En 16 los
#    Alas Express activos eran justo los publicados en el sitio (las copias del
#    B2B estaban archivadas y despublicadas), así que se reactivan los
#    publicados. Sin esto el B2C no tiene ningún método de envío.
# 2) Borra las vistas obsoletas del módulo antes de que Odoo las valide.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MODULE = 'outsideSports_alas_express'


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

    carriers = env['delivery.carrier'].search([
        ('delivery_type', '=', 'alas_express'),
        ('active', '=', False),
        ('is_published', '=', True),
    ])
    if carriers:
        carriers.write({'active': True})
    _logger.info("upgrade19 %s: métodos Alas Express reactivados %s", MODULE, carriers.ids)
