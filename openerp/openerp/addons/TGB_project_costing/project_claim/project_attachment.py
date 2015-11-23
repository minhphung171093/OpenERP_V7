
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_attachment(osv.osv):
    _name='project.attachment'
    _inherit='project.attachment'
            
    _columns = {
        'project_claim_id':fields.many2one('project.claim',string='Project Claim',),
        }
    
    _defaults={
    }

project_attachment()
