# Upgrade 16 -> 19 (Outside Sports): en 19 el formulario de reglas usa
# display_applied_on; las reglas por marca de 16 quedan con el valor por
# defecto ('1_product'). Se alinean con applied_on.


def migrate(cr, version):
    cr.execute("""
        UPDATE product_pricelist_item
           SET display_applied_on = '4_brand'
         WHERE applied_on = '4_brand'
    """)
