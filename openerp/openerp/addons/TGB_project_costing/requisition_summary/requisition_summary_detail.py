
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class requisition_summary_detail(osv.osv):
    _name='requisition.summary.detail'
    _columns = {
        'type':fields.many2one('requisition.type',string='Type',),
        'item_code':fields.many2one('product.product',string='Item Code',),
        'description':fields.related('item_code','description',string='Description',type='char'),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        'uom':fields.many2one('product.uom',string='UOM',),
        'pack_size':fields.many2one('product.packsize',string='Pack Size',),
        'no_of_pack':fields.float('No. of pack',digits_compute=dp.get_precision('Account'),),
        'pr_supplier_alloc_segments':fields.char('PR Supplier Alloc Segments',size=100,),
        'requisition_summary_id':fields.many2one('requisition.summary',string='Requsition Summary',),
        }
    
    _defaults={
    }

requisition_summary_detail()
