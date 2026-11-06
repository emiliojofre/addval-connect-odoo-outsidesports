# -*- coding: utf-8 -*-
{
    'name': 'Crédito interno de clientes (B2B)',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Pago con crédito interno en la tienda y gestión de saldos por cliente',
    'description': """
Reescritura para Odoo 19 (Outside Sports) del módulo de 16 "Customer Credit
Management for POS and Website" (BrowseInfo, con cambios de Addval). Mismo nombre
técnico y mismos modelos/campos para conservar saldos e historial:

* partner.credit (saldo por cliente, botón "Actualizar" para sumar crédito).
* update.credit.history / update.credit.history.payment (historial).
* res.partner: custom_credit (saldo) y allow_credit (permitir saldo negativo).
* Proveedor de pago "credit": solo visible para clientes con registro de
  crédito; al pagar descuenta el total del saldo, deja la transacción
  pendiente y confirma el pedido (como en 16). Sin saldo suficiente (y sin
  allow_credit) la transacción queda en error y el pedido sin confirmar.

No se porta (sin uso en producción): punto de venta, recarga de saldo desde la
web con "Credit Product", página /credit, recarga con asiento contable y la
reescritura de account.move._compute_amount.
""",
    'author': 'Outside Sports',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/payment_method_data.xml',
        'views/payment_templates.xml',
        'views/partner_credit_views.xml',
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'internal_credit_payment/static/src/interactions/post_processing.js',
        ],
    },
    'installable': True,
    'application': False,
}
