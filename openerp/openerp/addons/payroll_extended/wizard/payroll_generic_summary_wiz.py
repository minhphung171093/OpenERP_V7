# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import base64
try:
    import xlwt
except ImportError:
    xlwt = None
from cStringIO import StringIO
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT


def intcomma(self, cr, uid,n, thousands_sep,context):
    sign = '-' if n < 0 else ''
    n = str(abs(n)).split('.')
    dec = '' if len(n) == 1 else '.' + n[1]
    n = n[0]
    m = len(n)
    return sign + (str(thousands_sep[1]).join([n[0:m%3]] + [n[i:i+3] for i in range(m%3, m, 3)])).lstrip(str(thousands_sep[1])) + dec

class payroll_excel_export_summay(osv.osv_memory):
    
    _name = "payroll.excel.export.summay"
    
    def _get_payroll_excel_export_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        payslip_obj = self.pool.get('hr.payslip')
        hr_depart_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        res_user = self.pool.get("res.users").browse(cr, uid,uid,context=context)
        salary_rule = [rule.name for rule in self.pool.get("hr.salary.rule").browse(cr, uid, context.get("salary_rules_id"), context = context)]
        start_date = datetime.datetime.strptime(context.get("date_from"), DEFAULT_SERVER_DATE_FORMAT)
        start_date_formate = start_date.strftime('%d/%m/%Y')
        end_date = datetime.datetime.strptime(context.get("date_to"), DEFAULT_SERVER_DATE_FORMAT)
        end_date_formate = end_date.strftime('%d/%m/%Y')
        date_period = str(start_date_formate) + ' To ' + str(end_date_formate)
        alignment = xlwt.Alignment() # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.row(2).height = 500
        
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle() # Create Style
        border_style.borders = borders
        
        worksheet.write(0, 0, "Company Name :- " + res_user.company_id.name, header)
        worksheet.write(1, 0, "Payroll Summary Report :",header)
        worksheet.write(1, 2, "",header)
        worksheet.write(2, 0, "Period :",header)
        worksheet.write(2, 1, date_period ,header)
        
        row = 4
        col = 5
        worksheet.write(4, 0, "Employee No",border_style)
        worksheet.write(4, 1, "Employee Name",border_style)
        worksheet.write(4, 2, "Wage",border_style)
        worksheet.write(4, 3, "Wage To Pay",border_style)
        worksheet.write(4, 4, "Rate Per Hour",border_style)
        for rule in salary_rule:
            worksheet.write(row, col, rule,border_style)
            col +=1
            
        row +=2 
        
        result = {}
        total = {}
        employee_ids = employee_obj.search(cr, uid, [('id', 'in', context.get("employee_ids"))])
        res_lang_obj = self.pool.get('res.lang')
        res_lang_ids = res_lang_obj.search(cr, uid, [('code','=',res_user.context_lang)])
        thousands_sep = ","
        if res_lang_ids:
            thousands_sep = res_lang_obj._lang_data_get(cr, uid, res_lang_ids[0])
        tot_categ_cont_wage = tot_categ_cont_wage_to_pay = tot_categ_cont_rate_per_hour = 0.0
        for employee in employee_obj.browse(cr, uid, employee_ids):
            payslip_ids = payslip_obj.search(cr, uid, [('employee_id','=', employee.id),('date_from', '>=', context.get("date_from")), ('date_from','<=',context.get("date_to")), ('state', 'in', ['draft', 'done', 'verify'])])
            if not payslip_ids:
                continue
#            contact_id = payslip_obj.get_contract(cr, uid, employee, start_date, end_date)
#            basic_contract = False
#            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
#                for line in payslip.line_ids:
#                    if line.code == 'BASIC':
#                        basic_contract = True
#            contract_data = False
#            if contact_id:
#                contract_data = contract_obj.browse(cr, uid, contact_id[0], context=context)
#            if contract_data and basic_contract:
#                contract_wage = contract_data.wage
#                contract_wage_to_pay = contract_data.wage_to_pay
#                contract_rate_per_hour = contract_data.rate_per_hour
#            else:
            contract_wage = 0.0
            contract_wage_to_pay = 0.0
            contract_rate_per_hour = 0.0
            
            new_payslip_result = {}
            for rule in salary_rule:
                new_payslip_result.update({rule:0.00})
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                contract_rate_per_hour += payslip and payslip.contract_id and payslip.contract_id.rate_per_hour or 0.0
                for rule in payslip.details_by_salary_rule_category:
                    if rule.code == 'BASIC':
                        contract_wage += payslip and payslip.contract_id and payslip.contract_id.wage or 0.0
                        contract_wage_to_pay += payslip and payslip.contract_id and payslip.contract_id.wage_to_pay or 0.0
                    for set_rule in salary_rule:
                        rule_total = 0.00
                        if rule.name == set_rule:
                            rule_total += rule.total
                        new_payslip_result.update({set_rule: new_payslip_result.get(set_rule,0) + float(rule_total), 'conn': 100})
            payslip_result = {'department': employee.department_id.id or "Undefine",
                              'ename': employee.name, 
                              'eid': employee.user_id.login,
                              'wage': contract_wage,
                              'wage_to_pay': contract_wage_to_pay,
                              'rate_per_hour': contract_rate_per_hour}
            value_found = True
            for key,val in new_payslip_result.items():
                if val:
                    value_found = False
            if value_found:
                continue
            payslip_result.update(new_payslip_result)
            if payslip.employee_id.department_id:
                if payslip.employee_id.department_id.id in result:
                    result.get(payslip.employee_id.department_id.id).append(payslip_result)
                else:
                    result.update({payslip.employee_id.department_id.id: [payslip_result]})
            else:
                if 'Undefine' in result:
                    result.get('Undefine').append(payslip_result)
                else:
                    result.update({'Undefine': [payslip_result]})
        final_total = {'name':"Grand Total"}
        for rule in salary_rule:
            final_total.update({rule:0.0})
        for key, val in result.items():
            categ_cont_wage = categ_cont_wage_to_pay = categ_cont_rate_per_hour = 0.0
            style = xlwt.easyxf('font: bold 0')
            if key == 'Undefine':
                category_name = 'Undefine'
                category_id = 0
            else:
                category_name = hr_depart_obj.browse(cr, uid, key, context = context).name
                category_id = hr_depart_obj.browse(cr, uid, key, context = context).id
            total = {'categ_id':category_id,'name': category_name}
            for rule in salary_rule:
                total.update({rule:0.0})
            for line in val:
                for field in line:
                    if field in total:
                        total.update({field:  total.get(field) + line.get(field)})
            style1 = xlwt.easyxf()
            style1.num_format_str = '0.00'
            if total.get("name") == "Undefine":
                for payslip_result in result[total.get("name")]:
                    categ_cont_wage += payslip_result.get("wage")
                    tot_categ_cont_wage += payslip_result.get("wage")
                    categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    tot_categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    tot_categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    
                    contract_wage =  str(abs(payslip_result.get("wage")))
                    contract_wage= intcomma(self, cr, uid, float(contract_wage), thousands_sep, context)
                    contract_wage = contract_wage.ljust(len(contract_wage.split('.')[0])+3, '0')
                    
                    contract_wage_to_pay =  str(abs(payslip_result.get("wage_to_pay")))
                    contract_wage_to_pay= intcomma(self, cr, uid, float(contract_wage_to_pay), thousands_sep, context)
                    contract_wage_to_pay = contract_wage_to_pay.ljust(len(contract_wage_to_pay.split('.')[0])+3, '0')
                    
                    contract_rate_per_hour =  str(abs(payslip_result.get("rate_per_hour")))
                    contract_rate_per_hour= intcomma(self, cr, uid, float(contract_rate_per_hour), thousands_sep, context)
                    contract_rate_per_hour = contract_rate_per_hour.ljust(len(contract_rate_per_hour.split('.')[0])+3, '0')
                    
                    worksheet.write(row, 0, payslip_result.get("eid"))
                    worksheet.write(row, 1, payslip_result.get("ename"))
                    style.alignment = alignment
                    worksheet.write(row, 2, contract_wage, style)
                    worksheet.write(row, 3, contract_wage_to_pay, style)
                    worksheet.write(row, 4, contract_rate_per_hour, style)
                    col = 5
                    for rule in salary_rule:
                        split_total_rule = str(abs(payslip_result.get(rule)))
                        split_total_rule= intcomma(self, cr, uid, float(split_total_rule), thousands_sep, context)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
                        style.alignment = alignment
                        worksheet.write(row, col, split_total_rule, style)
                        col +=1
                    row +=1
            else:
                for payslip_result in result[total.get("categ_id")]:
                    categ_cont_wage += payslip_result.get("wage")
                    tot_categ_cont_wage += payslip_result.get("wage")
                    categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    tot_categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    tot_categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    
                    contract_wage =  str(abs(payslip_result.get("wage")))
                    contract_wage= intcomma(self, cr, uid, float(contract_wage), thousands_sep, context)
                    contract_wage = contract_wage.ljust(len(contract_wage.split('.')[0])+3, '0')
                    
                    contract_wage_to_pay =  str(abs(payslip_result.get("wage_to_pay")))
                    contract_wage_to_pay= intcomma(self, cr, uid, float(contract_wage_to_pay), thousands_sep, context)
                    contract_wage_to_pay = contract_wage_to_pay.ljust(len(contract_wage_to_pay.split('.')[0])+3, '0')
                    
                    contract_rate_per_hour =  str(abs(payslip_result.get("rate_per_hour")))
                    contract_rate_per_hour= intcomma(self, cr, uid, float(contract_rate_per_hour), thousands_sep, context)
                    contract_rate_per_hour = contract_rate_per_hour.ljust(len(contract_rate_per_hour.split('.')[0])+3, '0')
                    
                    worksheet.write(row, 0, payslip_result.get("eid"))
                    worksheet.write(row, 1, payslip_result.get("ename"))
                    style.alignment = alignment
                    worksheet.write(row, 2, contract_wage, style)
                    worksheet.write(row, 3, contract_wage_to_pay, style)
                    worksheet.write(row, 4, contract_rate_per_hour, style)
                    col = 5
                    for rule in salary_rule:
                        split_total_rule =  str(abs(payslip_result.get(rule)))
                        split_total_rule= intcomma(self, cr, uid, float(split_total_rule), thousands_sep, context)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
                        style.alignment = alignment
                        worksheet.write(row, col, split_total_rule, style)
                        col +=1
                    row +=1
            
            borders = xlwt.Borders()
            borders.top = xlwt.Borders.MEDIUM
            borders.bottom = xlwt.Borders.MEDIUM
            border_top = xlwt.XFStyle() # Create Style
            border_top.borders = borders
            style = xlwt.easyxf('font: bold 1')
            style.num_format_str = '0.00'
            
            worksheet.write(row, 0, str("Total "+total["name"]) ,style)
            worksheet.write(row, 1, "" ,style)
            col = 5 
            
            categ_cont_wage =  str(abs(categ_cont_wage))
            categ_cont_wage= intcomma(self, cr, uid, float(categ_cont_wage), thousands_sep, context)
            categ_cont_wage = categ_cont_wage.ljust(len(categ_cont_wage.split('.')[0])+3, '0')
            
            categ_cont_wage_to_pay =  str(abs(categ_cont_wage_to_pay))
            categ_cont_wage_to_pay= intcomma(self, cr, uid, float(categ_cont_wage_to_pay), thousands_sep, context)
            categ_cont_wage_to_pay = categ_cont_wage_to_pay.ljust(len(categ_cont_wage_to_pay.split('.')[0])+3, '0')
            
            categ_cont_rate_per_hour =  str(abs(categ_cont_rate_per_hour))
            categ_cont_rate_per_hour= intcomma(self, cr, uid, float(categ_cont_rate_per_hour), thousands_sep, context)
            categ_cont_rate_per_hour = categ_cont_rate_per_hour.ljust(len(categ_cont_rate_per_hour.split('.')[0])+3, '0')
            
            style.alignment = alignment
            worksheet.write(row, 2, categ_cont_wage, style)
            worksheet.write(row, 3, categ_cont_wage_to_pay, style)
            worksheet.write(row, 4, categ_cont_rate_per_hour, style)
            for rule in salary_rule:
                rule_total = 0.0
                split_total_rule = str(abs(total[rule]))
                split_total_rule= intcomma(self, cr, uid, float(split_total_rule), thousands_sep, context)
                split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
                style.alignment = alignment
                worksheet.write(row, col, split_total_rule, style)
                rule_total = final_total[rule] + total[rule]
                final_total.update({rule:rule_total})
                col +=1
            row +=2
        
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        border_total = xlwt.XFStyle() # Create Style
        border_total.borders = borders
        row +=1
        worksheet.write(row, 0, final_total["name"] ,style)
        worksheet.write(row, 1, "" ,border_total)
        col = 5
        
        tot_categ_cont_wage =  str(abs(tot_categ_cont_wage))
        tot_categ_cont_wage= intcomma(self, cr, uid, float(tot_categ_cont_wage), thousands_sep, context)
        tot_categ_cont_wage = tot_categ_cont_wage.ljust(len(tot_categ_cont_wage.split('.')[0])+3, '0')
        
        tot_categ_cont_wage_to_pay =  str(abs(tot_categ_cont_wage_to_pay))
        tot_categ_cont_wage_to_pay= intcomma(self, cr, uid, float(tot_categ_cont_wage_to_pay), thousands_sep, context)
        tot_categ_cont_wage_to_pay = tot_categ_cont_wage_to_pay.ljust(len(tot_categ_cont_wage_to_pay.split('.')[0])+3, '0')
        
        tot_categ_cont_rate_per_hour =  str(abs(tot_categ_cont_rate_per_hour))
        tot_categ_cont_rate_per_hour= intcomma(self, cr, uid, float(tot_categ_cont_rate_per_hour), thousands_sep, context)
        tot_categ_cont_rate_per_hour = tot_categ_cont_rate_per_hour.ljust(len(tot_categ_cont_rate_per_hour.split('.')[0])+3, '0')
        
        style.alignment = alignment
        worksheet.write(row, 2, tot_categ_cont_wage, style)
        worksheet.write(row, 3, tot_categ_cont_wage_to_pay, style)
        worksheet.write(row, 4, tot_categ_cont_rate_per_hour, style)
        for rule in salary_rule:
            split_total_rule =  str(abs(final_total[rule]))
            split_total_rule= intcomma(self, cr, uid, float(split_total_rule), thousands_sep, context)
            split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
            style.alignment = alignment
            worksheet.write(row, col, split_total_rule, style)
            col +=1
        row +=1
        
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)

    _columns = {
        "file":fields.binary("Click On Save As Button To Download File", readonly=True),
        "name":fields.char("Name" , size=32)
    }
    
    _defaults = {
        'name':"generic summary.xls",
        'file': _get_payroll_excel_export_data
    }

class payroll_generic_summary_wizard(osv.osv):

    _name = 'payroll.generic.summary.wizard'

    _columns = {
                'date_from': fields.date('Date From'),
                'date_to': fields.date('Date To'),
                'employee_ids': fields.many2many('hr.employee', 'ihrms_hr_employee_payroll_rel4','emp_id4','employee_id','Employee Name'),
                'export_report' : fields.selection([('excel','Excel')] , "Export"),
                'salary_rule_ids': fields.many2many('hr.salary.rule', 'ihrms_hr_employe_salary_rule_rel','salary_rule_id','employee_id','Employee payslip')
    }

    _defaults = {
        'export_report': "excel"
        }

    def print_order(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        if data.get("export_report") == "excel":
            context.update({'employee_ids': data['employee_ids'], 'salary_rules_id':data['salary_rule_ids'],'date_from': data['date_from'], 'date_to': data['date_to']})
            return {
              'name': _('Binary'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'payroll.excel.export.summay',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
              }

payroll_generic_summary_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: