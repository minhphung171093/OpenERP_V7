# -*- coding: utf-8 -*-

from report import report_sxw
import datetime

class ppd_hr_cheque_summary_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(ppd_hr_cheque_summary_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
            'get_info': self.get_info,
            'datetime': datetime,
            'get_totalrecord': self.get_totalrecord,
            'get_total': self.get_total,
        })
    
    def get_info(self, name, date_from, date_to):
        payslip_obj = self.pool.get('hr.payslip')
        hr_depart_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        hr_department_search_id =  hr_depart_obj.search(self.cr, self.uid, [])
        result = {}
        payslip_data= {}
        department_info = {}
        final_result = {}
        
        employee_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', name), ('department_id', '=', False)])
        department_total_amount = 0.0
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            payslip_ids = []
            if employee.bank_detail_ids:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('pay_by_cheque', '=', True), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
            else:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
            net = 0.0
            if not payslip_ids:
                continue
            cheque_number = ''
            for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                if not cheque_number:
                    cheque_number = payslip.cheque_number
                if not payslip.employee_id.department_id.id:
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
                             
            payslip_data = {
                            'employee_id': employee.user_id and employee.user_id.login or ' ',
                            'employee_name':employee.name or ' ',
                            'cheque_number':cheque_number,
                            'amount':net,
            }
            department_total_amount += net
            if 'Undefine' in result:
                result.get('Undefine').append(payslip_data)
            else:
                result.update({'Undefine': [payslip_data]})
        department_total = {'total': department_total_amount, 'department_name': "Total Undefine"}
        if 'Undefine' in department_info:
            department_info.get('Undefine').append(department_total)
        else:
            department_info.update({'Undefine': [department_total]})
        
        for hr_department in hr_depart_obj.browse(self.cr, self.uid, hr_department_search_id):
            employee_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', name), ('department_id', '=', hr_department.id)])
            department_total_amount = 0.0
            for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
                payslip_ids = []
                if employee.bank_detail_ids:
                    payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                               ('employee_id', '=' , employee.id), ('pay_by_cheque', '=', True), ('state', 'in', ['draft', 'done', 'verify'])])
                    if payslip_id:
                        payslip_ids.append(payslip_id[0])
                else:
                    payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                               ('employee_id', '=' , employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                    if payslip_id:
                        payslip_ids.append(payslip_id[0])
                net = 0.0
                if not payslip_ids:
                    continue
                cheque_number = ''
                for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                    if not cheque_number:
                        cheque_number = payslip.cheque_number
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
                
                payslip_data = {
                                'employee_id': employee.user_id and employee.user_id.login or ' ',
                                'employee_name': employee.name or ' ',
                                'cheque_number': cheque_number,
                                'amount': net,
                }
                department_total_amount += net
                if hr_department.id in result:
                    result.get(hr_department.id).append(payslip_data)
                else:
                    result.update({hr_department.id: [payslip_data]})
            department_total = {'total': department_total_amount, 'department_name': "Total "+hr_department.name}
            if hr_department.id in department_info:
                department_info.get(hr_department.id).append(department_total)
            else:
                department_info.update({hr_department.id: [department_total]})
        for key, val in result.items():
            final_result[key] = {'lines': val, 'departmane_total': department_info[key] }
        return final_result.values()
    
    def get_total(self, name, date_from, date_to):
        payslip_obj = self.pool.get('hr.payslip')
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', name)])
        total_ammount = 0
        payslip_ids = []
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            if employee.bank_detail_ids:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('pay_by_cheque', '=', True), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
            else:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
        if payslip_ids:
            for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                for line in payslip.line_ids:
                    if line.code == 'NET':
                        total_ammount+=line.total
        return total_ammount
    
    def get_totalrecord(self, name, date_from, date_to):
        payslip_obj = self.pool.get('hr.payslip')
        employee_obj = self.pool.get('hr.employee')
        emp_list = []
        employee_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', name)])
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            payslip_ids = []
            if employee.bank_detail_ids:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('pay_by_cheque', '=', True), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
            else:
                payslip_id = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                           ('employee_id', '=' , employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id[0])
            if payslip_ids:
                emp_list.append(employee.id)
        return len(emp_list)
    
report_sxw.report_sxw('report.ppd_cheque_summary_receipt','hr.payslip','addons/payroll_extended/report/hr_cheque_summary_report.rml',parser=ppd_hr_cheque_summary_report)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

