
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_project(osv.osv):
    _name='project.project'
    _inherit='project.project'
            
    _columns = {
        'project_class_id':fields.many2one('project.class',string='Project Class',),
        'project_category_id':fields.many2one('project.category',string='Project Category',),
        }
    
    _defaults={
    }

project_project()
