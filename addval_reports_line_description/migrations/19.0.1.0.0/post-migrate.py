# Upgrade 16 -> 19 (Outside Sports): el servicio de upgrade de Odoo desactiva
# las vistas personalizadas que fallan con las plantillas de 19. En 16 estaban
# activas las del presupuesto y las líneas agregadas del albarán (la de la
# solicitud de presupuesto ya estaba desactivada y se deja así). Con el arch de
# 19 ya cargado se reactivan.
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

REACTIVATE = [
    'addval_reports_line_description.report_saleorder_document_inherit',
    'addval_reports_line_description.stock_report_delivery_aggregated_move_lines_inherit',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    for xmlid in REACTIVATE:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view and not view.active:
            view.active = True
            _logger.info("upgrade19 addval_reports_line_description: reactivada %s", xmlid)
