# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): en 16 cada tarifa tenía "Política de
# descuento" (incluido en el precio / mostrar precio público y descuento). En 19
# ese campo no existe y la tienda tacha el precio público siempre que la regla
# sea de porcentaje o de fórmula con descuento. Esta casilla recupera el
# comportamiento de 16 en la tienda: solo se muestra el precio tachado en las
# tarifas que la tengan marcada.
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    show_public_price_on_shop = fields.Boolean(
        string="Mostrar precio público y descuento en la tienda",
        help="Si está marcada, la tienda muestra el precio público tachado junto al precio "
             "de esta tarifa. Si no, solo el precio final (descuento incluido en el precio), "
             "como la política \"Descuento incluido en el precio\" de Odoo 16.",
    )
