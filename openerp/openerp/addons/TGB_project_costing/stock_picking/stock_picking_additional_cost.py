
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_additional_cost(osv.osv):
    _name='stock.picking.additional.cost'
    _inherit='stock.move'
            
    _columns = {
        'supplier_id':fields.many2one('res.partner',string='Supplier',),
        'service_id':fields.many2one('stock.picking.service',string='Service',),
        'currency_id':fields.many2one('res.currency',string='Ccy',),
        'exchange_rate':fields.float('Exch Rate',digits_compute=dp.get_precision('Account'),),
        'charge_amt':fields.float('Charge Amt',digits_compute=dp.get_precision('Account'),),
        'charge_home_amt':fields.float('Charge Home Amt',digits_compute=dp.get_precision('Account'),),
        'cost_dist_mtd':fields.selection([('weight','weight'),],'cost',),
        'stock_picking_id':fields.many2one('stock.picking',string='Stock Picking',),
        'stock_picking_in_id':fields.many2one('stock.picking.in',string='Stock Picking In',),
        'stock_picking_out_id':fields.many2one('stock.picking',string='Stock Picking Out',),
        }
    
    _defaults={
    }

stock_picking_additional_cost()
