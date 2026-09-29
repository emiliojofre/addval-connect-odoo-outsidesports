# -*- coding: utf-8 -*-
{
   'name': "Customizaciones para Outsidesports",

    'summary': """
        Se añaden customizaciones específicas""",

    'description': """
        En el website se añade el SKU y el PVP en los productos. 
        Se incluye la opción de calcular tarifas por marca.
        La descripción de la línea de factura muestra solo el nombre del producto.
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Product",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': [
        'base',
        'sale',
        'account',
        'product',
        'website_product_brands'
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'views/pricelist_item.xml',
        
    ],



    'installable': True,
    'application': True,
    'auto_install': False,
}
