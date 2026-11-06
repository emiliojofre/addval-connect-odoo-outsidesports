# -*- coding: utf-8 -*-
{
    'name': "Comunas por Región",

    'summary': """
        Comunas con dominio en regiones (addval_cl_communes)""",

    'description': """
        Comunas con dominio en regiones (addval_cl_communes)
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Partner",
    "license": "Other proprietary",
    'version': '19.0.1.0.0',
    
    'data': [
        'data/res_city.xml',
        'data/res_country.xml',
    ],
    
    'depends': [
        'base', 
        'base_address_extended'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
}
