import time
from report import report_sxw
from osv import osv
import pooler
from datetime import date

class tax_invoice_report_indonesia(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(tax_invoice_report_indonesia, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_address': self.get_address,
            'get_address_cust': self.get_address_cust,
        })
        
    def get_address(self,data):
        if data.company_id.partner_id.street or data.company_id.partner_id.street2 or data.company_id.partner_id.city:
            address = data.company_id.partner_id.street + ',' + data.company_id.partner_id.street2 + ',' + data.company_id.partner_id.city
            return address
        return ''
    
    def get_address_cust(self,data):
        if data.partner_id.street or data.partner_id.street2 or data.partner_id.city:
            address = data.partner_id.street + ',' + data.partner_id.street2 + ',' + data.partner_id.city
            return address
        return ''
    
report_sxw.report_sxw('report.tax.invoice.indonesia','tax.invoice','project_costing_sinar/report/tax_invoice_report_indonesia.rml', parser=tax_invoice_report_indonesia,header=False)
