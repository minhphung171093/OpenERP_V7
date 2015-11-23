import time
from report import report_sxw
from osv import osv

class public_holiday_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        
        super(public_holiday_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
report_sxw.report_sxw('report.public.holidays',
                       'hr.holiday.public', 
                       'addons/hr_holiday_extended/report/public_holiday_report.rml',
                       parser=public_holiday_report)

