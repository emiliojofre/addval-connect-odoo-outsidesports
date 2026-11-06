# -*- coding: utf-8 -*-
{
    'name': "Cuenta Analítica Pedidos Web",
    'summary': "Cuenta analítica por sitio web en las líneas de los pedidos web",
    'description': """
Cuenta Analítica Pedidos Web (addval_website_sale).

Port a Odoo 19 (Outside Sports): cada sitio web tiene su "Cuenta analítica
Website" y las líneas de sus pedidos llevan 100 % en esa cuenta (B2B
Distribuidores / B2C Consumidor). En 16 se hacía en sale_get_order (ya no
existe); ahora en el cálculo de la distribución analítica de la línea.
""",
    'author': "Addval Connect",
    'website': "http://www.addval.cl",
    'category': "Sale",
    'license': "Other proprietary",
    'version': '19.0.1.0.0',
    'depends': ['website_sale'],
    'data': [
        'views/website.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
