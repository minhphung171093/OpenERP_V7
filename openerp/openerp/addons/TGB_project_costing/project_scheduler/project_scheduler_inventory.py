
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_scheduler_inventory(osv.osv):
    _name='project.scheduler.inventory'
    _columns = {
        'phase_desc':fields.char('Phase Desc',size=100,),
        'remarks':fields.char('Remarks',size=100,),
        'phase_group_id':fields.many2one('project.phase.group',string='Phase Group',),
        'total_qty':fields.float('Total Qty',digits_compute=dp.get_precision('Account'),),
        'scheduled_qty':fields.float('Scheduled Qty',digits_compute=dp.get_precision('Account'),),
        'remaining_qty':fields.float('Remaining Qty',digits_compute=dp.get_precision('Account'),),
        'max_material_lead_time':fields.integer('Max material Lead Time (days)',),
        'project_scheduler_id':fields.many2one('project.scheduler',string='Project scheduler',),
        }
    
    _defaults={
    }

project_scheduler_inventory()
