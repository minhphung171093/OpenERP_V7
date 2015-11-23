# -*- coding: utf-8 -*-

import time

from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"
    def _get_tgb_payment(self,cr,uid,ids,a,b,context={}):
        val = {}
        for detail in self.browse(cr,uid,ids):
            val[detail.id]={}
            val[detail.id]['gross_payment'] = detail.day_wage+detail.incentive+detail.extra
            val[detail.id]['net_payment'] = val[detail.id]['gross_payment']-detail.advance_deduction
        return val
    def onchange_tgb_payment(self,cr,uid,ids,day_wage,incentive,extra,advance_deduction,context={}):
        value = {}
        value['gross_payment'] = day_wage+incentive+extra
        value['net_payment'] = value['gross_payment']-advance_deduction
        print 'value', value
        return {'value':value}

    _columns = {
        'shift':fields.integer('Shift',size=2),
        'box':fields.integer('Box',size=100),
        'day_wage':fields.float('Day Wage',digits_compute=dp.get_precision('Account')),
        'incentive':fields.float('Incentive',digits_compute=dp.get_precision('Account')),
        'extra':fields.float('Extra',digits_compute=dp.get_precision('Account')),
        'gross_payment':fields.function(_get_tgb_payment,type='float',digits_compute=dp.get_precision('Account'), string='Gross Payment', multi='tgb_payment',
                                        store={
                                        'hr.analytic.timesheet': (lambda self, cr,uid,ids,c: ids, ['day_wage','incentive','extra','advance_deduction'], 10),}),
        'advance_deduction':fields.float('Advance/ Deduction',digits_compute=dp.get_precision('Account')),
        'net_payment':fields.function(_get_tgb_payment,type='float',digits_compute=dp.get_precision('Account'), string='Net Payment', multi='tgb_payment',store={
                                        'hr.analytic.timesheet': (lambda self, cr,uid,ids,c: ids, ['day_wage','incentive','extra','advance_deduction'], 10),}),
    }

hr_analytic_timesheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
