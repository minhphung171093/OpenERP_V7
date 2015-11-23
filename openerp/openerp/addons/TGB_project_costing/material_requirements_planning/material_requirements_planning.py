
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class material_requirements_planning(osv.osv):
    _name='material.requirements.planning'
    _columns = {
        'resource_planning_period_ids':fields.one2many('resource.planning.period','requirement_planning_id',string='Resource Planning Period',),
        'weekly_resource_requirement_ids':fields.one2many('weekly.resource.requirement','requirement_planning_id',string='Weekly Resource Requirements',),
        'resource_requirement_by_mps_vou_ids':fields.one2many('resource.requirement.by.mps.vou','requirement_planning_id',string='Resource Requirement By MPS Voucher',),
        }
    
    _defaults={
    }

material_requirements_planning()
