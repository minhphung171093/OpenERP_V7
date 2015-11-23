
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_attachment(osv.osv):
    _name='project.attachment'
    _inherit='project.attachment'
            
    _columns = {
        'project_billing_id':fields.many2one('account.invoice',string='Project billing',),
        }
    
    _defaults={
    }

project_attachment()
