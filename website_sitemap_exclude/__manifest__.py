{
    'name': 'Website Sitemap Exclude',
    'summary': 'Saca del sitemap.xml las URLs técnicas (pagos, crédito, info)',
    'description': """
Filtra las URLs de /sitemap.xml cuyo path empieza con alguno de los prefijos
del parámetro de sistema website_sitemap_exclude.prefixes (separados por coma).
Las rutas siguen funcionando; solo dejan de anunciarse a los buscadores.
""",
    'version': '16.0.1.0.0',
    'category': 'Website/Website',
    'author': 'Outside Sports',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'application': False,
}
