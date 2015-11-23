
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class Test(osv.osv):
    _name='stock.picking'
    _inherit='stock.picking'
            
    def _get_sub_description(self, cr, uid, ids, name, arg, context={}):
        return True
    
    _columns = {
        'shipment_no':fields.char('Shipment No',size=20,),
        'supplier_do_date':fields.date('Supplier DO Date',),
        'currency_id':fields.many2one('res.currency',string='Currency',),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),),
        'require_stock_return':fields.selection([('yes_to_be_test','Yes To be test'),('no','No'),],'Require Stock Return',),
        'stock_issue_emp_line':fields.one2many('stock.issue.employee','stock_issue_id',string='Stock Issue Employee',),
        'sub_des':fields.function(_get_sub_description,string='Subject Description',type='char',size=50,),
        'product_code':fields.related('product_id','default_code',string='Inventory Description',type='char'),
        }
    
    _defaults={
    }

Test()
