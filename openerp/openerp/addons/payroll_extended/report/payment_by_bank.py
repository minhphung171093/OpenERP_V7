# -*- coding: utf-8 -*-

from report import report_sxw

class payment_by_bank_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(payment_by_bank_report,self).__init__(cr,uid,name,context=context)

report_sxw.report_sxw('report.paymentbybank_receipt','hr.payslip','addons/payroll_extended/report/payment_by_bank_report.rml',parser=payment_by_bank_report)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

