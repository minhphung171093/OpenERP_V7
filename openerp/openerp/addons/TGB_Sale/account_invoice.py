# -*- coding: utf-8 -*-
__author__ = 'Phamkr'
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
        'is_fixed':fields.boolean('Is fixed amount'),
    }
    _defaults={
        'is_fixed':False,
    }
account_invoice()