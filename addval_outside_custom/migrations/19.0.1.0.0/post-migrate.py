# Upgrade 16 -> 19 (Outside Sports):
# 1) En 19 el formulario de reglas usa display_applied_on; las reglas por marca
#    de 16 quedan con el valor por defecto ('1_product'). Se alinean con
#    applied_on.
# 2) "Política de descuento" de la tarifa (16) -> casilla
#    show_public_price_on_shop: marcada en las tarifas que en 16 tenían
#    "Mostrar al cliente el precio público y el descuento" (without_discount).
import logging

_logger = logging.getLogger(__name__)

# Respaldo si el upgrade de Odoo ya eliminó la columna discount_policy: tarifas
# con without_discount en producción el 12-11-2026.
WITHOUT_DISCOUNT_IDS = (13,)  # Sugerido a público


def migrate(cr, version):
    cr.execute("""
        UPDATE product_pricelist_item
           SET display_applied_on = '4_brand'
         WHERE applied_on = '4_brand'
    """)

    cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'product_pricelist' AND column_name = 'discount_policy'
    """)
    if cr.fetchone():
        cr.execute("""
            UPDATE product_pricelist SET show_public_price_on_shop = TRUE
             WHERE discount_policy = 'without_discount'
         RETURNING id
        """)
    else:
        cr.execute("""
            UPDATE product_pricelist SET show_public_price_on_shop = TRUE
             WHERE id IN %s
         RETURNING id
        """, [WITHOUT_DISCOUNT_IDS])
    _logger.info("upgrade19 addval_outside_custom: tarifas con precio público en tienda %s",
                 [r[0] for r in cr.fetchall()])
