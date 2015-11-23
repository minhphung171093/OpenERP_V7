
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class weekly_resource_requirement(osv.osv):
    _name='weekly.resource.requirement'
    _columns = {
        'material_inventory_code':fields.char('Material Inventory Code',size=20,),
        'description':fields.char('Description',size=100,),
        'location_code':fields.many2one('stock.location',string='Location Code',),
        'source_type':fields.char('Source Type',size=20,),
        'material_lead_time':fields.float('Material Lead Time',digits_compute=dp.get_precision('Account'),),
        'qty_hand_available':fields.float('Qty On Hand Available',digits_compute=dp.get_precision('Account'),),
        'qty_order_available':fields.float('Qty On Order Available',digits_compute=dp.get_precision('Account'),),
        'total_qty_available':fields.float('Total Qty Available',digits_compute=dp.get_precision('Account'),),
        'total_qty_required':fields.float('Total Qty Required',digits_compute=dp.get_precision('Account'),),
        'qty_allocated':fields.float('Qty Allocated',digits_compute=dp.get_precision('Account'),),
        'qty_unplanned':fields.float('Qty Unplanned',digits_compute=dp.get_precision('Account'),),
        'total_to_raise':fields.float('Total PR Qty to Raise',digits_compute=dp.get_precision('Account'),),
        'pr_bom_parts':fields.float('PR By BOM Parts',digits_compute=dp.get_precision('Account'),),
        'sel':fields.float('Sel',digits_compute=dp.get_precision('Account'),),
        'requirement_planning_id':fields.many2one('material.requirements.planning',string='Requirement ',),
        }
    
    _defaults={
    }

weekly_resource_requirement()
