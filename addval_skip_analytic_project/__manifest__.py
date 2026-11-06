# -*- coding: utf-8 -*-
{
    'name': "Addval Skip Analytic Project (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports): en 16 evitaba que cada proyecto creara una
cuenta analítica. En 19 el proyecto solo crea cuenta analítica si está
instalada la hoja de horas (hr_timesheet), que no se usa, así que el módulo
queda vacío. Se mantiene solo para que el upgrade no falle; desinstalar
después del paso a 19.
""",
    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Hidden",
    "license": "Other proprietary",
    'version': '19.0.1.0.0',
    'depends': ['project'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
