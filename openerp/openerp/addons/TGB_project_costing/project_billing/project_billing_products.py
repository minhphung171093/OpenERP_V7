
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_products(osv.osv):
    _name='project.billing.product'
    _columns = {
        'type':fields.char('Type',size=5,),
        'product_id':fields.many2one('product.product',string='Item description',),
        'remark':fields.char('Remarks',size=100,),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        'uom_id':fields.many2one('product.uom',string='UOM',),
        'unit_price':fields.float('Unit Price',digits_compute=dp.get_precision('Account'),),
        'disc_per':fields.float('Disc %',digits_compute=dp.get_precision('Account'),),
        'dis_amount':fields.float('Disc Amount',digits_compute=dp.get_precision('Account'),),
        'total_amount':fields.float('Total Amount',digits_compute=dp.get_precision('Account'),),
        'budgeted_unit_cost':fields.float('Budgeted Unit Cost',digits_compute=dp.get_precision('Account'),),
        'mark_up_per':fields.float('Markup %',digits_compute=dp.get_precision('Account'),),
        'quoted_amount':fields.float('Quoted Amt',digits_compute=dp.get_precision('Account'),),
        'project_billing_id':fields.many2one('account.invoice',string='Project Billing',),
        }
    
    _defaults={
    }

project_billing_products()
