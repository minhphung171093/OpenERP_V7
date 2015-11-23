# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import netsvc
import datetime
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
import pytz

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'add_discount_percent':fields.float("Discount Percent"),
        'discount_added':fields.boolean("Discount Added"),
    }

    def add_percent_discount(self,cr,uid,ids,context=None):
        for invoice in self.browse(cr,uid,ids,context):
            if not invoice.discount_added:
                self.write(cr,uid,[invoice.id],{'discount_added':True})
                for line in invoice.invoice_line:
                    self.pool.get('account.invoice.line').write(cr,uid,[line.id],
                                                                {'discount':line.discount+invoice.add_discount_percent})
        return True

    def remove_percent_discount(self,cr,uid,ids,context=None):
        for invoice in self.browse(cr,uid,ids,context):
            if invoice.discount_added:
                self.write(cr,uid,[invoice.id],{'discount_added':False})
                for line in invoice.invoice_line:
                    self.pool.get('account.invoice.line').write(cr,uid,[line.id],
                                                                {'discount':line.discount-invoice.add_discount_percent})
        return True
    _default = {
        'discount_added':False,
        'add_percent_discount':0,

    }