# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'type_id':fields.many2one('tgb.product.type','Type'),
        'brand_id':fields.many2one('tgb.product.brand','Brand'),
    }

product_product()

class product_type(osv.osv):
    _name='tgb.product.type'
    _columns={
        'name':fields.char('Name',size=255)
    }
product_type()

class product_brand(osv.osv):
    _name='tgb.product.brand'
    _columns={
        'name':fields.char('Name',size=255)
    }
product_brand()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

