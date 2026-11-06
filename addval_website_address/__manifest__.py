# -*- coding: utf-8 -*-
{
    'name': "Addval Website Address",
    'summary': "Comuna (res.city) en el formulario de dirección del sitio web para Chile",
    'description': """
Port a Odoo 19 (Outside Sports): en el formulario de dirección estándar
(portal.address_form_fields, usado en el checkout y en Mi cuenta) la ciudad
se elige desde las comunas de addval_cl_communes cuando el país es Chile.
La comuna rellena ciudad, código postal y región al guardar.
""",
    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Website/eCommerce",
    "license": "Other proprietary",
    'version': '19.0.1.0.0',
    'depends': ['base', 'website_sale', 'addval_cl_communes'],
    'data': [
        'views/website_sale_address.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'addval_website_address/static/src/js/website_sale.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
