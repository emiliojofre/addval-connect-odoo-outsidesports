# -*- coding: utf-8 -*-
{
    'name': 'Accounting Configurations (Outside Sports)',
    'summary': 'Cuenta de activo o gasto por proveedor en facturas de compra',
    'description': """
Reemplazo en Odoo 19 del módulo addval_accounting de Addval (Odoo 16), escrito
por Outside Sports. Mantiene el mismo nombre técnico para conservar los datos.

Se conserva:
- "Cuenta Activo o Gasto" en el contacto (property_account_assets_or_expenses_id,
  por compañía). En facturas de proveedor, las líneas usan esa cuenta.
  Cambio respecto a 16: ya no se aplica a facturas de cliente.

Se deja atrás (no hace falta en 19 o no se usaba):
- PDF de factura propio y "Factura Cedible": se usa el PDF estándar de
  l10n_cl_edi y su copia cedible ("Invoice PDF copy (Chile)").
- Prioridad de DTE, validación e impresión masiva, moneda/precio original,
  documento 820, filtro por cuenta, widget de dos decimales.
""",
    'author': 'Outside Sports',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'version': '19.0.1.0.0',
    'depends': ['account'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
