# -*- coding: utf-8 -*-
{
    'name': "Addval Purchase (obsoleto en 19)",
    'summary': "Sin efecto en Odoo 19: se puede desinstalar",
    'description': """
Port a Odoo 19 (Outside Sports). En 16 daba el formato Addval a la solicitud/orden de compra y enlazaba facturas
de proveedor con su OC por referencia 801 (en producción las referencias 801
traen números del proveedor, no de la OC, así que nunca enlazaba). En 19 se
usan los informes estándar.
Se mantiene vacío solo para que el upgrade no falle; desinstalar después del
paso a 19.
""",
    'author': "Outside Sports",
    'category': "Hidden",
    'license': "LGPL-3",
    'version': '19.0.1.0.0',
    'depends': ['purchase'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
