
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_carrier(osv.osv):
    _name='stock.picking.carrier'
    _inherit='stock.picking.out'
            
    _columns = {
        'party_name':fields.char('Party Name',size=100,),
        'party_code':fields.char('Party Code',size=20,),
        }
    
    _defaults={
    }

stock_picking_carrier()
