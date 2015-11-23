# -*- coding: utf-8 -*-

{
    "name" : "Elite Report Module",
    "version" : "0.1",
    "author" : "Son Pham",
    "category" : "Generic Modules",
    "depends" : ['base',
                 'sale',
                 'purchase',
                 'account',
                 ],
    "description": "TGB Elite edit report",
    "data": ['sale_report.xml',
             'purchase_report.xml',
             'sale_order_view.xml',
             'account_report.xml',
             ],
    'installable': True,
    'auto_install': False,
}
