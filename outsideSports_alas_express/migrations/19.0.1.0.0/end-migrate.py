# Upgrade 16 -> 19 (Outside Sports): red de seguridad que repite al FINAL de
# la actualización la reactivación de los métodos Alas Express publicados.
# OJO: en las bases de PRUEBA de Odoo.sh quedan archivados igualmente porque la
# neutralización (delivery/data/neutralize.sql) archiva todos los métodos de
# proveedores externos después de actualizar; en producción no hay
# neutralización. Para probar en una base de prueba, reactivarlos a mano.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    carriers = env['delivery.carrier'].search([
        ('delivery_type', '=', 'alas_express'),
        ('active', '=', False),
        ('is_published', '=', True),
    ])
    if carriers:
        carriers.write({'active': True})
    _logger.info("upgrade19 outsideSports_alas_express (end): reactivados %s", carriers.ids)
