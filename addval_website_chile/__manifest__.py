# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT, Teléfono y Precio IVA Incluido',
    'version': '19.0.1.0.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': (
        'Checkout B2C de Chile: RUT obligatorio y validado, teléfono +56, '
        'registro de clientes y precio con IVA incluido solo en el sitio B2C.'
    ),
    'description': """
Port a Odoo 19 (Outside Sports):
- El precio con IVA incluido del B2C es ahora el ajuste estándar por sitio
  "Visualización de impuestos" (website.show_line_subtotals_tax_selection);
  el post-migrate lo deja en "IVA incluido" para el sitio 3 y "sin IVA" en
  los demás. Se eliminan los overrides de precios y el JS/CSS que los parcheaba.
- La comuna la aporta addval_website_address en el formulario estándar.
- Las tarjetas de dirección de 19 ya permiten archivar direcciones: se quita
  el botón y la ruta propios.
- Ya no depende de internal_credit_payment (solo se declaraba para forzar
  el orden de los controladores de 16).
""",
    'depends': [
        'addval_website_address',
        'website_sale',
        'eq_website_default_code',
        'auth_signup',
    ],
    'data': [
        'views/website_sale_address.xml',
        'views/website_sale_product.xml',
        'views/website_auth_signup.xml',
    ],
    'installable': True,
    'auto_install': False,
}
