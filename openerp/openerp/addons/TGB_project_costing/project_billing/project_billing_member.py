
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_member(osv.osv):
    _name='project.billing.member'
    _columns = {
        'user_id':fields.many2one('res.users',string='Member',),
        'project_billing_id':fields.many2one('account.invoice',string='project Billing',),
        }
    
    _defaults={
    }

project_billing_member()
