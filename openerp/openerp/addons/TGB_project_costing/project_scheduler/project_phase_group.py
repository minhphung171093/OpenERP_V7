
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_phase_group(osv.osv):
    _name='project.phase.group'
    _columns = {
        'name':fields.char('Name',size=20,),
        }
    
    _defaults={
    }

project_phase_group()
