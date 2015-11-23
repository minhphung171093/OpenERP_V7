# -*- coding: utf-8 -*-

from report import report_sxw
import datetime

class payslip_sample_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(payslip_sample_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                        'get_basic': self.get_basic,
                        'get_cpf': self.get_cpf,
                        'datetime': datetime,
                        'get_lvd': self.get_lvd,
                        'get_allowance': self.get_allowance,
                        'get_netwage': self.get_netwage,
                        'get_grosswage': self.get_grosswage,
        })
       
    def get_basic(self, main_id):
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.code == 'BASIC':
                return line.total
        return 0
    
    def get_cpf(self, main_id):
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.code == 'CPF':
                return line.total
        return 0
    
    def get_lvd(self, main_id):
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.code == 'LVD':
                return line.total
        return 0
    
    def get_allowance(self, main_id):
        result_deduction = []
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.category_id.code == 'ALW':
                res = {
                       'name': line.name,
                       'total': line.total,
                    }
                result_deduction.append(res)
        return result_deduction
    
    def get_netwage(self, main_id):
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.code == 'NET':
                return line.total
        return 0
    
    def get_grosswage(self, main_id):
        line_obj = self.pool.get('hr.payslip')
        line_id = line_obj.browse(self.cr, self.uid, main_id)
        for line in line_id.line_ids:
            if line.code == 'GROSS':
                return line.total
        return 0
    
report_sxw.report_sxw('report.payslipsample_receipt','hr.payslip','addons/payroll_extended/report/payslip_sample_report.rml',parser=payslip_sample_report)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

