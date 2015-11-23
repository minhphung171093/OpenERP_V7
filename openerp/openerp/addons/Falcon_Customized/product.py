# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'custom_list1': fields.many2one('falcon.custom.list1', 'Custom List 1'),
        'custom_list2': fields.many2one('falcon.custom.list2', 'Custom List 2'),
        'custom_list3': fields.many2one('falcon.custom.list3', 'Custom List 3'),
        'reorder_quantity':fields.integer('Reorder Quantity'),
    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

