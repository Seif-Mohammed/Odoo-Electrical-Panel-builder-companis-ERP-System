{
    'name': 'Simple Inventory Authorization',
    'version': '1.0',
    'summary': 'Simple authorization system for inventory movements',
    'description': """
        Simple module to manage inventory with echnical office and manufacturing departments.
    """,
    'author': 'Seif Mohamed Ramadan',
    'depends': ['base' ,'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_auth_views.xml',
        'views/technical_office_views.xml',
        'views/manufacturing_views.xml',
        'reports/bom_report.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'app1/static/src/css/technical_office_style.css',
        ],
    },
    'installable': True,
    'application': True,
}