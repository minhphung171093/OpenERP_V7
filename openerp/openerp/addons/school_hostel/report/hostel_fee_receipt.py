# -*- coding: utf-8 -*-

from openerp.report import report_sxw

class hostel_fee_receipt(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(hostel_fee_receipt,self).__init__(cr,uid,name,context=context)

report_sxw.report_sxw('report.hostel_fee_slip','hostel.student','addons/school_hostel/report/hostel_fee_receipt.rml',parser=hostel_fee_receipt)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=