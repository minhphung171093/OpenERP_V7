
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_project(osv.osv):
    _name='project.project'
    _inherit='project.project'
            
    _columns = {
        'project_type':fields.many2one('project.type',string='Project Type',),
        }
    
    _defaults={
    }

project_project()
