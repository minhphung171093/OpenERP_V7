# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    def _get_retail_price(self,cr,uid,ids,a,b,context={}):
        res = {}
        for product in self.browse(cr,uid,ids):
            res[product.id] = {
                'yen_price':0,
                'pound_price':0,
                'usd_price':0,
            }
            cur_obj = self.pool.get('res.currency')
            jpy_cur = cur_obj.search(cr,uid,[('name','=','JPY')])[0]
            jpy_cur = cur_obj.browse(cr,uid,jpy_cur)
            pound_cur = cur_obj.search(cr,uid,[('name','=','GBP')])[0]
            pound_cur = cur_obj.browse(cr,uid,pound_cur)
            usd_cur = cur_obj.search(cr,uid,[('name','=','USD')])[0]
            usd_cur = cur_obj.browse(cr,uid,usd_cur)
            print 'product.price', product.list_price, jpy_cur, pound_cur, usd_cur
            res[product.id]['yen_price'] = cur_obj.round(cr, uid, jpy_cur, product.list_price*90.7206)
            res[product.id]['pound_price'] = cur_obj.round(cr, uid, pound_cur, product.list_price*0.485492)
            res[product.id]['usd_price'] = cur_obj.round(cr, uid, usd_cur, product.list_price*0.761471)
        return res
    _columns = {
        'tgb_length': fields.char('Length',size=10),
        'tgb_width': fields.char('Width',size=10),
        'tgb_size': fields.char('Size',size=10),
        'tgb_weight': fields.char('Weight',size=10),
        'yen_price': fields.function(_get_retail_price, string='Yen Price', type='float', multi='cur', readonly=True),
        'pound_price': fields.function(_get_retail_price, string='Yen Price', type='float', readonly=True, multi='cur'),
        'usd_price': fields.function(_get_retail_price, string='Yen Price', type='float', readonly=True, multi='cur'),
        'tgb_brand':fields.many2one('tgb.brand','Brand'),
        'tgb_type':fields.many2one('tgb.type','Product Type'),
        'suggested_price':fields.float('Suggested Price', digits_compute=dp.get_precision('Product'))
    }

product_product()

class tgb_brand(osv.osv):
    _name = 'tgb.brand'
    _columns = {
        'name':fields.char('Name', size=255),
    }
tgb_brand()

class tgb_type(osv.osv):
    _name = 'tgb.type'
    _columns = {
        'name':fields.char('Name', size=255),
    }
tgb_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

