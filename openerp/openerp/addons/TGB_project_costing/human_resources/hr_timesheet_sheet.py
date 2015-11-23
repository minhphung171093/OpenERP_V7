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

class hr_timesheet_sheet(osv.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    def add_to_invoice(self,cr,uid,ids,context={}):
        for timesheet in self.browse(cr,uid,ids,context):
            if not timesheet.invoice_exists:
                invoice_id = None
                if timesheet.sale_order_id:
                    invoice_ids  = self.pool.get('account.invoice').search(cr,uid,[('sale_order_id','=',timesheet.sale_order_id.id)])
                    if invoice_ids and len(invoice_ids)>0:
                        invoice_id=invoice_ids[0]
                hour_rate = 0

                if timesheet.contract_id:
                    if timesheet.contract_id.rate_per_hour>0:
                        hour_rate = timesheet.contract_id.rate_per_hour

                if invoice_id and hour_rate>0:
                    description = self.name_get(cr,uid,timesheet.id)[0][1]
                    qty = timesheet.total_attendance
                    unit_price = hour_rate
                    new_line = self.pool.get('account.invoice.line').create(cr,uid,{'name':"Timesheet/" +description + " of "+timesheet.employee_id.name,
                                                                         'quantity':qty,
                                                                         'price_unit':unit_price,
                                                                         'invoice_id':invoice_id,})
                    if new_line:
                        self.write(cr,uid,timesheet.id,{'invoice_exists':True}),
        return True

    _columns = {
        'sale_order_id':fields.many2one('sale.order','Project Order',domain=[('state','!=','draft')]),
        'contract_id':fields.many2one('hr.contract','Contract'),
        'invoice_exists':fields.boolean('Billing added'),
    }

    _defaults = {
        'invoice_exists':False,
    }
hr_timesheet_sheet()