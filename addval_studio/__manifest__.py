# -*- coding: utf-8 -*-
{
    'name': "Addval Studio (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports). En 16 cambiaba el manejo de traducciones de Studio. Sin datos propios; en 19
no se necesita.
Se mantiene vacío solo para que el upgrade no falle; desinstalar después del
paso a 19.
""",
    'author': "Outside Sports",
    'category': "Hidden",
    'license': "LGPL-3",
    'version': '19.0.1.0.0',
    'depends': ['web_studio'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
