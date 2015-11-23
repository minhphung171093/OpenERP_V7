
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_allocation_detail(osv.osv):
    _name='stock.picking.allocation.detail'
    _inherit='stock.move'
            
    _columns = {
        'stock_picking_id':fields.many2one('stock.picking',string='Stock Picking',),
        'stock_picking_in_id':fields.many2one('stock.picking.in',string='Stock Picking In',),
        'stock_picking_out_id':fields.many2one('stock.picking.out',string='Stock Picking Out',),
        'allocation_no':fields.char('Allocation No.',size=10,),
        'type':fields.char('Type',size=5,),
        'voucher_no':fields.char('Voucher No.',size=20,),
        'phase_sequence_no':fields.char('Phase Sequence No.',size=20,),
        'schedule_no':fields.float('Schedule No.',digits_compute=dp.get_precision('Account'),),
        'line_no':fields.float('Line No.',digits_compute=dp.get_precision('Account'),),
        'requested_alloc_qty':fields.float('Requested Alloc Qty',digits_compute=dp.get_precision('Account'),),
        'ost_qty':fields.float('Ost Qty',digits_compute=dp.get_precision('Account'),),
        'requested_alloc_no_of_pack':fields.float('Requested Alloc No. of pack',digits_compute=dp.get_precision('Account'),),
        'alloc_qty':fields.float('Alloc Qty',digits_compute=dp.get_precision('Account'),),
        }
    
    _defaults={
    }

stock_picking_allocation_detail()
