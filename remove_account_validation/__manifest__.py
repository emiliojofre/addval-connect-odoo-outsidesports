# -*- coding: utf-8 -*-
{
    'name': "Remove Account Validation (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports): en 16 anulaba la restricción que impedía usar
la misma cuenta en entrada, salida y valoración de stock en las categorías.
En 19 esa restricción ya no existe (valoración de inventario rehecha), así que
el módulo queda vacío. Se mantiene solo para que el upgrade no falle;
desinstalar después del paso a 19.
""",
    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Hidden",
    "license": "Other proprietary",
    'version': '19.0.1.0.0',
    'depends': ['stock_account'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
