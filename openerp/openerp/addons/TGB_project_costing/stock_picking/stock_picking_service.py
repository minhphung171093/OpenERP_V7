
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_service(osv.osv):
    _name='stock.picking.service'
    _inherit='stock.move'
            
    _columns = {
        'service_code':fields.char('Service Code',size=20,),
        'description':fields.char('Service Description',size=100,),
        }
    
    _defaults={
    }

stock_picking_service()
