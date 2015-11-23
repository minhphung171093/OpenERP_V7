
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_move(osv.osv):
    _name='stock.move'
    _inherit='stock.move'
            
    _columns = {
        'type':fields.char('Type',size=5,),
        'remarks_description':fields.related('product_id','description',string='Remarks Description',type='char'),
        'source_voucher_no':fields.char('Source Voucher No.',size=20,),
        'pack size':fields.many2one('product.packsize',string='Pack Size',),
        'no_of_pack':fields.float('No. of pack',digits_compute=dp.get_precision('Account'),),
        'qty_req':fields.float('Qty Req',digits_compute=dp.get_precision('Account'),),
        'no_of_pack_req':fields.float('No Of Pack Req',digits_compute=dp.get_precision('Account'),),
        'ost_qty':fields.float('Ost Qty',digits_compute=dp.get_precision('Account'),),
        'complete':fields.boolean('Complete',),
        'serial_no':fields.char('Serial No',size=20,),
        'lot':fields.char('Lots',size=5,),
        }
    
    _defaults={
    }

stock_move()
