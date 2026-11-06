# -*- coding: utf-8 -*-
{
    'name': "Addval Sale (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports). En 16 añadía el campo 'Fecha OC cliente' (sin datos en producción) y el formato
de cotización/pedido de Addval (basado en addval_accounting de Addval, ya no
existe). En 19 se usa el informe estándar de pedido.
Se mantiene vacío solo para que el upgrade no falle; desinstalar después del
paso a 19.
""",
    'author': "Outside Sports",
    'category': "Hidden",
    'license': "LGPL-3",
    'version': '19.0.1.0.0',
    'depends': ['sale'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
