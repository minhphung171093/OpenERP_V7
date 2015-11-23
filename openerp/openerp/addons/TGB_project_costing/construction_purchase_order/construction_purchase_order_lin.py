
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class construction_purchase_order_line(osv.osv):
    _name='construction.purchase.order.line'
    def _get_amount(self,cr,uid,ids,fields,args,context={}):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            amount = line.qty*line.unit_cost

            res[line.id] = {
                'tax':(amount-line.discount_amount)*line.sales_tax.amount,
                'total':amount-line.discount_amount,
            }
        return res
    _columns = {
        'type':fields.char('Type',size=5,),
        'product_id':fields.many2one('product.product',string='Item Code',),
        'remarks_description':fields.related('product_id','description',string='Remarks Description',type='char'),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        'uom':fields.many2one('product.uom',string='UOM',),
        'pack_size':fields.many2one('product.packsize',string='Pack Size',),
        'no_of_pack':fields.integer('No. of pack',),
        'sales_tax':fields.many2one('account.tax',string='Sales Tax',),
        'unit_cost':fields.float('Unit Cost',digits_compute=dp.get_precision('Account'),),
        'location_id':fields.many2one('stock.location',string='Location',),
        'discount_percent':fields.float('Discount Percent',digits_compute=dp.get_precision('Account'),),
        'discount_amount':fields.float('Discount Amount',digits_compute=dp.get_precision('Account'),),
        'total':fields.function(_get_amount,string='Total',multi='amount',digits_compute=dp.get_precision('Account'),),
        'construction_purchase_order_id':fields.many2one('construction.purchase.order','Purchase Order'),
        'tax':fields.function(_get_amount,type='float',string='Tax amount',multi='amount'),
        }
    
    _defaults={
        'qty':1,
    }

construction_purchase_order_line()
