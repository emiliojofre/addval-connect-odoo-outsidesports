# -*- coding: utf-8 -*-
{
    'name': "Actualización Partner LibreDTE (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports). En 16 añadía el botón 'Actualizar Datos SII' (API de LibreDTE) en contactos y un
cron, inactivo desde octubre de 2024. En 19 no se porta.
Se mantiene vacío solo para que el upgrade no falle; desinstalar después del
paso a 19.
""",
    'author': "Outside Sports",
    'category': "Hidden",
    'license': "LGPL-3",
    'version': '19.0.1.0.0',
    'depends': ['account'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
