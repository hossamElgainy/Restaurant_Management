{
    'name': "Restaurant Management",
    'author': "Hossam Elganiny",
    'category': 'Restaurant Management',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/restaurant_table_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}