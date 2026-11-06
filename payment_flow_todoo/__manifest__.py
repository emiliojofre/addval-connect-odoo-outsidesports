# -*- coding: utf-8 -*-

{
    'name': 'Flow Payment Provider',
    'version': "19.0.1.0.0",
    'summary': 'Chilean Flow Payment Provider',
    'description': """Payment Provider: Chilean Flow Payment Provider.

Port a Odoo 19 (Outside Sports): API de proveedores de 19 (_process,
_apply_updates, payment.method "Flow"), mismas URLs de notificación y retorno.
""",
    'license': 'AGPL-3',
    'author': "ToDOO Web (www.todooweb.com)",
    'category': 'Accounting/Payment Providers',
    'website': "https://todooweb.com/",
    'contributors': [
        "Antonio David <antoniodavid8@gmail.com>",
        "Equipo Dev <devtodoo@gmail.com>",
        "Edgar Naranjo <edgarnaranjof@gmail.com>",
    ],
    'support': 'devtodoo@gmail.com',
    'depends': [
        'payment',
        'payment_flow_currency_todoo',
    ],
    'data': [
        'views/payment_flow_templates.xml',
        'views/payment_provider.xml',
        'views/payment_transaction.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'images': [
        'static/description/screenshot_pay.png'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 59.99,
    'currency': 'EUR',
}
