{
    'name': 'Website Checkout Signup Offer',
    'summary': 'Ofrece crear una cuenta en el paso de dirección del checkout B2C',
    'description': """
Muestra en /shop/address, a los visitantes sin sesión del sitio B2C, un bloque
con botones para crear una cuenta o iniciar sesión. Ambos vuelven al checkout y
se puede seguir comprando como invitado.
""",
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'author': 'Outside Sports',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'auth_signup'],
    'data': [
        'views/website_sale_address.xml',
    ],
    'installable': True,
    'application': False,
}
