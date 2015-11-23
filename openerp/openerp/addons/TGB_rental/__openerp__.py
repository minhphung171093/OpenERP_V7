# -*- coding: utf-8 -*-

{
    "name" : "TGB Rental Module",
    "version" : "0.1",
    "author" : "Son Pham",
    "category" : "Generic Modules",
    "depends" : ['base',
                 'stock',
                 'sale',
                 'purchase',
                 'procurement',
                 'stock_location',
                 'sale_stock',
                 'delivery',
                 'account',
                 ],
    "description": "TGB Rental Module",
    "data": [
        "delivery_view.xml",
        "product_view.xml",
         "repair_view.xml",
         'group.xml',
         'ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
