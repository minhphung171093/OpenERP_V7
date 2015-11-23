# -*- coding: utf-8 -*-

from report import report_sxw

class payment_by_cheque_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(payment_by_cheque_report,self).__init__(cr,uid,name,context=context)

report_sxw.report_sxw('report.paymentbycheque_receipt','hr.payslip','addons/payroll_extended/report/payment_by_cheque_report.rml',parser=payment_by_cheque_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

