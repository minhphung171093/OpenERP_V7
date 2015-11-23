
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class resource_planning_period(osv.osv):
    _name='resource.planning.period'
    _columns = {
        'requirement_planning_id':fields.many2one('material.requirements.planning',string='Plan',),
        'week_no':fields.integer('Week No',),
        'po_deadline_from':fields.date('PO Deadline From',),
        'po_deadline_to':fields.date('PO Deadline To',),
        'status':fields.selection([('no_requirement','No Requirement'),('requirement','Requirement'),],'Status',),
        }
    
    _defaults={
    }

resource_planning_period()
