# -*- coding: utf-8 -*-
{
    'name': "shipment",

    'summary': """
       Shipment""",

    'description': """
        Shipment description
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'vehicle', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/shipment_view.xml',
        'views/vehicle_views.xml',
        'wizard/shipment_wizard.xml',
        'data/sequences.xml',
    ],
}
