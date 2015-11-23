# -*- coding: utf-8 -*-

from report import report_sxw
import datetime

class ppd_bank_summary_receipt(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(ppd_bank_summary_receipt,self).__init__(cr,uid,name,context=context)
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
        bank_obj = self.pool.get('hr.bank.details')
        hr_department_search_id =  hr_depart_obj.search(self.cr, self.uid, [])
        result = {}
        payslip_data= {}
        department_info = {}
        final_result = {}
        
        employee_ids = employee_obj.search(self.cr, self.uid, [('bank_detail_ids','!=',False), ('id', 'in', name), ('department_id', '=', False)])
        department_total_amount = 0.0
        new_employee_ids = []
        if employee_ids:
            bank_ids = bank_obj.search(self.cr, self.uid, [('bank_emp_id', 'in', employee_ids)], order="bank_name, bank_code, branch_code")
            for bank in bank_obj.browse(self.cr, self.uid, bank_ids):
                if bank.bank_emp_id.id not in new_employee_ids:
                    new_employee_ids.append(bank.bank_emp_id.id)
            blank_emp_ids = list(set(employee_ids).difference(set(new_employee_ids)))
            new_employee_ids += blank_emp_ids
        
        for employee in employee_obj.browse(self.cr, self.uid, new_employee_ids):
            payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                                 ('employee_id', '=' , employee.id), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
            net = 0.0
            if not payslip_ids:
                continue
            for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                if not payslip.employee_id.department_id.id:
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
            print "::::::::::::", employee, employee.bank_detail_ids
            payslip_data = {
                            'bank_name':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_name or '',
                            'bank_id':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_code or '',
                            'branch_id':employee.bank_detail_ids and employee.bank_detail_ids[0].branch_code or '',
                            'employee_id':employee and employee.user_id and employee.user_id.login or ' ',
                            'employee_name':employee.name,
                            'account_number':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_ac_no or '',
                            'amount':net,
            }
            department_total_amount += net
            if 'Undefine' in result:
                result.get('Undefine').append(payslip_data)
            else:
                result.update({'Undefine': [payslip_data]})
        department_total = {'total': department_total_amount, 'department_name': 'Total Undefine'}
        
        if 'Undefine' in department_info:
            department_info.get('Undefine').append(department_total)
        else:
            department_info.update({'Undefine': [department_total]})
        
        for hr_department in hr_depart_obj.browse(self.cr, self.uid, hr_department_search_id):
            employee_ids = employee_obj.search(self.cr, self.uid, [('bank_detail_ids','!=',False), ('id', 'in', name), ('department_id', '=', hr_department.id)])
            department_total_amount = 0.0
            new_employee_ids = []
            if employee_ids:
                bank_ids = bank_obj.search(self.cr, self.uid, [('bank_emp_id', 'in', employee_ids)], order="bank_name, bank_code, branch_code")
                for bank in bank_obj.browse(self.cr, self.uid, bank_ids):
                    if bank.bank_emp_id.id not in new_employee_ids:
                        new_employee_ids.append(bank.bank_emp_id.id)
                blank_emp_ids = list(set(employee_ids).difference(set(new_employee_ids)))
                new_employee_ids += blank_emp_ids
            for employee in employee_obj.browse(self.cr, self.uid, new_employee_ids):
                payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                               ('employee_id', '=' , employee.id), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
                net = 0.0
                if not payslip_ids:
                    continue
                for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
                print "::::::::::::", employee, employee.bank_detail_ids
                payslip_data = {
                            'bank_name':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_name or '',
                            'bank_id':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_code or '',
                            'branch_id':employee.bank_detail_ids and employee.bank_detail_ids[0].branch_code or '',
                            'employee_id':employee and employee.user_id and employee.user_id.login or ' ',
                            'employee_name':employee.name,
                            'account_number':employee.bank_detail_ids and employee.bank_detail_ids[0].bank_ac_no or '',
                            'amount':net,
                }
                department_total_amount += net
                if hr_department.id in result:
                    result.get(hr_department.id).append(payslip_data)
                else:
                    result.update({hr_department.id: [payslip_data]})
            department_total = {'total': department_total_amount, 'department_name': "Total " + hr_department.name}
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
        employee_ids = employee_obj.search(self.cr, self.uid, [('bank_detail_ids','!=',False), ('id', 'in', name)])
        total_ammount = 0
        payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to), ('pay_by_cheque','=',False), ('employee_id', 'in' , employee_ids), ('state', 'in', ['draft', 'done', 'verify'])])
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
        employee_ids = employee_obj.search(self.cr, self.uid, [('bank_detail_ids','!=',False), ('id', 'in', name)])
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', date_from), ('date_from','<=',date_to),
                                                                 ('employee_id', '=' , employee.name), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
            if payslip_ids:
                emp_list.append(employee.id)
        return len(emp_list)

report_sxw.report_sxw('report.ppd_bank_summary_receipt','hr.payslip','addons/payroll_extended/report/hr_bank_summary_report.rml',parser=ppd_bank_summary_receipt)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

