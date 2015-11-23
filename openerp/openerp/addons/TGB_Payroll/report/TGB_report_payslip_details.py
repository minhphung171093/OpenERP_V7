#-*- coding:utf-8 -*-

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class TGB_payslip_details_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(TGB_payslip_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_total': self._get_total,
            'total':self._get_total2,
        })
    def _get_total2(self):
        print 'total ', self._total
        return self._total
    _total = {}

    def _get_total(self,payslip):
        shift = 0
        box = 0
        day_wage = 0
        incentive = 0
        extra = 0
        gross_payment = 0
        advance_deduction = 0
        net_payment = 0
        for detail in payslip.tgb_hr_payroll_detail_ids:
            shift+=detail.shift
            box+=detail.box
            day_wage+=detail.day_wage
            incentive+=detail.incentive
            extra+=detail.extra
            gross_payment+=detail.gross_payment
            advance_deduction+=detail.advance_deduction
            net_payment+=detail.net_payment

        val = {'shift':shift,
                'box':box,
                'day_wage':day_wage,
                'incentive':incentive,
                'extra':extra,
                'gross_payment':gross_payment,
                'advance_deduction':advance_deduction,
                'net_payment':net_payment}
        self._total = val
        return val



report_sxw.report_sxw('report.TGB.paylip.details', 'hr.payslip', 'TGB_Payroll/report/TGB_report_payslip_details.rml', parser=TGB_payslip_details_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
