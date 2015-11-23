# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import openerp.addons.decimal_precision as dp
import os
from openerp import modules

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'partner_multi_company_line': fields.one2many('partner.multi.company','partner_id','Partner Multi Company'),
    }
    
res_partner()

class partner_multi_company(osv.osv):
    _name = "partner.multi.company"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='cascade'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'receivable_acc_id': fields.many2one('account.account', 'Account Receivable', required=True),
        'payable_acc_id': fields.many2one('account.account', 'Account Payable', required=True),
    }
    
    
partner_multi_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
