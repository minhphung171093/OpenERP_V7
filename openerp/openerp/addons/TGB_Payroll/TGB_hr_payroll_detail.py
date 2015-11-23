# -*- coding: utf-8 -*-


from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class TGB_hr_payslip_detail(osv.osv):
    _name = 'tgb.hr.payslip.detail'
    _columns = {
        'payslip_id':fields.many2one('hr.payslip','Payslip'),
        'timesheet_detail_id':fields.many2one('hr.analytic.timesheet'),
        'shift':fields.related('timesheet_detail_id','shift',type='integer',size=2,string='Shift'),
        'box':fields.related('timesheet_detail_id','box',type='integer',size=100,string='Box'),
        'day_wage':fields.related('timesheet_detail_id','day_wage',type='float',digits_compute=dp.get_precision('Account'),string='Day Wage'),
        'incentive':fields.related('timesheet_detail_id','incentive',type='float',digits_compute=dp.get_precision('Account'),string='Incentive'),
        'extra':fields.related('timesheet_detail_id','extra',type='float',digits_compute=dp.get_precision('Account'),string='Extra'),
        'gross_payment':fields.related('timesheet_detail_id','gross_payment',type='float',digits_compute=dp.get_precision('Account'),string='Gross Payment'),
        'advance_deduction':fields.related('timesheet_detail_id','advance_deduction',type='float',digits_compute=dp.get_precision('Account'),string='Advance/ Deduction'),
        'net_payment':fields.related('timesheet_detail_id','net_payment',type='float',digits_compute=dp.get_precision('Account'),string='Net Payment'),
        'date':fields.related('timesheet_detail_id','date',type='date',string='Date'),
    }

TGB_hr_payslip_detail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
