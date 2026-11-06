# Upgrade 16 -> 19 (Outside Sports).
# Las copias por sitio (COW) de las vistas de los módulos de tienda de terceros
# no tienen xmlid, así que Odoo las aplica siempre al validar, aunque su módulo
# aún no se haya actualizado. Con el arch de 16 rompen la validación de los
# módulos que se actualizan antes. Se desactivan aquí (este módulo se carga
# primero) y website_product_brands las reactiva en su post-migrate, cuando
# todos ya tienen el arch de 19.
import logging

_logger = logging.getLogger(__name__)

PARAM = 'outside_upgrade19.cow_view_ids'
PREFIXES = (
    'website_base_filter_attribute.',
    'website_stock_availability_filter.',
    'website_product_brands.',
    'eq_website_default_code.',
    'odoo_website_product_label.',
)


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_ui_view
           SET active = false
         WHERE website_id IS NOT NULL
           AND active
           AND arch_updated IS NOT TRUE
           AND split_part(key, '.', 1) || '.' = ANY(%s)
     RETURNING id
    """, (list(PREFIXES),))
    ids = [r[0] for r in cr.fetchall()]
    cr.execute("""
        INSERT INTO ir_config_parameter (key, value, create_date, write_date)
        VALUES (%s, %s, now(), now())
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (PARAM, ','.join(map(str, ids))))
    _logger.info("upgrade19: %s vistas COW de tienda desactivadas temporalmente: %s", len(ids), ids)
