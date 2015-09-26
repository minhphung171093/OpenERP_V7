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

class product_product(osv.osv):
    _inherit = "product.product"
    _order = 'default_code'
    _columns = {
        'product_multi_company_line': fields.one2many('product.multi.company','product_id','Product Multi Company'),
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('default_code',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('name_template',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
product_product()

class product_multi_company(osv.osv):
    _name = "product.multi.company"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'income_acc_id': fields.many2one('account.account', 'Income Account', required=True),
        'expense_acc_id': fields.many2one('account.account', 'Expense Account', required=True),
        'customer_tax_ids': fields.many2many('account.tax', 'product_multi_company_cus_tax_ref', 'product_multi_company_id', 'tax_id', 'Customer Taxes', required=True),
        'supplier_tax_ids': fields.many2many('account.tax', 'product_multi_company_sup_tax_ref', 'product_multi_company_id', 'tax_id', 'Supplier Taxes', required=True),
    }
    
    
product_multi_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
