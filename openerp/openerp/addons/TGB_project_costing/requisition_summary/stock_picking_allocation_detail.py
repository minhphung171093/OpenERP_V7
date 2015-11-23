
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_allocation_detail(osv.osv):
    _name='stock.picking.allocation.detail'
    _inherit='stock.picking.allocation.detail'
            
    _columns = {
        'requisition_summary_id':fields.many2one('requisition.summary',string='Requsition Summary',),
        }
    
    _defaults={
    }

stock_picking_allocation_detail()
