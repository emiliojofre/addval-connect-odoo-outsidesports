# Upgrade 16 -> 19 (Outside Sports): repite la reactivación de los métodos
# Alas Express publicados al FINAL de la actualización (después de cargar todos
# los módulos). En el build de Odoo.sh del 06-11 el post-migrate los reactivó
# pero quedaron archivados de nuevo durante la misma carga, y el B2C se quedó
# sin métodos de envío.
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
