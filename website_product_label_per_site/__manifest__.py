{
    'name': 'Website Product Label per Website',
    'summary': 'Labels de producto distintas por sitio web (B2B / B2C)',
    'description': """
Extiende odoo_website_product_label (BrowseInfo) para elegir una label
distinta para cada sitio web. La label general del producto se sigue usando
en los sitios que no tengan una label propia.
""",
    'version': '16.0.1.0.0',
    'category': 'Website/eCommerce',
    'author': 'Outside Sports',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'odoo_website_product_label'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_website_label_views.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': False,
}
