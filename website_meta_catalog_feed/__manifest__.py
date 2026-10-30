{
    'name': 'Website Meta Catalog Feed',
    'summary': 'Feed XML de productos para el catálogo de Meta (Instagram/Facebook Shopping)',
    'description': """
Publica /meta-catalog.xml con una fila por variante publicada: precio de la
tarifa del sitio (con IVA en el B2C, vía addval_website_chile), stock, imagen,
marca y enlace directo a la ficha con la variante seleccionada.

Commerce Manager lo lee como "feed de datos programado". Solo responde en los
sitios cuyo id está en el parámetro website_meta_catalog_feed.website_ids
(por defecto el B2C, id 3), para no exponer la tarifa de distribuidores.
""",
    'version': '16.0.1.0.0',
    'category': 'Website/eCommerce',
    'author': 'Outside Sports',
    'license': 'LGPL-3',
    'depends': ['website_sale_stock', 'website_product_brands'],
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'application': False,
}
