{
    'name': "Restaurant Management",
    'author': "Hossam Elganiny",
    'category': 'Restaurant Management',
    'version': '0.1',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/restaurant_table_view.xml',
        'views/restaurant_menu_category_view.xml',
        'views/restaurant_menu_item_view.xml',
        'views/restaurant_customer_view.xml',
        'data/ir_sequence_data.xml',
        'views/restaurant_order_view.xml',
        'views/restaurant_reservation_view.xml',
        'views/restaurant_menu_modifier_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'restaurant_management/static/src/componants/kitchen/kitchen_screen.js',
            'restaurant_management/static/src/componants/kitchen/kitchen_screen.xml',
            'restaurant_management/static/src/componants/kitchen/kitchen_screen.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}