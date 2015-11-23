# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import base64
import xlwt
from cStringIO import StringIO
import tools
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import parser
from dateutil.relativedelta import relativedelta
import calendar

class export_payroll_exchequer_report(osv.osv_memory):

    _name = 'export.payroll.exchequer.report'

    def _get_payroll_exchequer_report_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        workbook = xlwt.Workbook()
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: name Arial, bold off, height 200; align: wrap on;')
        header2 = xlwt.easyxf('borders: right double, bottom_color black; font: name Arial, bold off, height 200; align: wrap on;')
        header_center = xlwt.easyxf('font: name Arial, bold off, height 200; align: wrap on, vert center, horiz center;')
        border_style = xlwt.easyxf('pattern: pattern solid, fore_colour white; borders: left double, right double, top double, bottom double, bottom_color black; font: bold on, height 200, color black; align: wrap off')
        style_font_red = xlwt.easyxf('font: name Arial, bold on, color red, height 200; align: wrap off;')
        style_font_red1 = xlwt.easyxf('borders: bottom double, bottom_color black; font: name Arial, bold on, color red, height 200; align: wrap off;')
        style_font_red2 = xlwt.easyxf('borders: right double, bottom_color black; font: name Arial, bold on, color red, height 200; align: wrap off;')
        style_font_red3 = xlwt.easyxf('borders: right double, bottom double, bottom_color black; font: name Arial, bold on, color red, height 200; align: wrap off;')
        style_font_red2_right = xlwt.easyxf('borders: right double, bottom_color black; font: name Arial, bold on, color red, height 200; align: wrap off, vert center, horiz right;')
        
        bottom_blue = xlwt.easyxf('borders: bottom double, bottom_color blue; font: name Arial, bold off, height 200; align: wrap on;')
        top_blue = xlwt.easyxf('borders: top double, top_color blue; font: name Arial, bold off, height 200; align: wrap on;')
        left_blue = xlwt.easyxf('borders: left double, left_color blue; font: name Arial, bold off, height 200; align: wrap on, vert center, horiz center;')
        
        header.num_format_str = '#,##0.00'
        header2.num_format_str = '#,##0.00'
        border_style.num_format_str = '#,##0.00'
        style_font_red.num_format_str = '#,##0.00'
        bottom_blue.num_format_str = '#,##0.00'
        
        period_obj = self.pool.get('account.period')
        payslip_obj = self.pool.get('hr.payslip')
        salary_report_for_exchequer_obj = self.pool.get('salary.report.for.exchequer.glcode')
        res_company_obj = self.pool.get('res.company')
        sale_order_line_obj = self.pool.get('sale.order.line')
        hr_salary_rule_glcode_obj = self.pool.get('hr.salary.rule.glcode')
        employee_category_obj = self.pool.get('hr.employee.category')
        
        emp_categ_ids = employee_category_obj.search(cr, uid, [])
        company_id = res_company_obj.search(cr, uid, [])
        company_name = currency_symbol = ''
        if company_id:
            company_name = res_company_obj.browse(cr, uid, company_id[0]).name
            currency_symbol = res_company_obj.browse(cr, uid, company_id[0]).currency_id.symbol
        date_from = period_obj.browse(cr, uid, context.get('period_from')[0]).date_start
        date_to = period_obj.browse(cr, uid, context.get('period_from')[0]).date_stop
        date_formate = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
        year = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%Y')
        month = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%m')
        month_year = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%B %Y')
        
        date_from1 = datetime.datetime.strptime(str(date_from), DEFAULT_SERVER_DATE_FORMAT)
        previous_month_obj = parser.parse(date_from1.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
        total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
        first_day_of_previous_month = datetime.datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
        last_day_of_previous_month = datetime.datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
        final_first_day_of_pre_month = datetime.datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        final_last_day_of_pre_month = datetime.datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        
        salary_back_selection_list = [('saved_back_cpf', 'SAVED BACK CPF'), ('saved_back_salary', 'SAVED BACK SALARY')]
        Flag = False
        for salary_back in salary_back_selection_list:
            total_amount = 0.00
            worksheet = workbook.add_sheet(salary_back[1])
            worksheet.col(0).width = 4000
            worksheet.col(1).width = 15000
            row = 0
            worksheet.write(row, 1, '', header2)
            row += 1
            worksheet.write(row, 0, 'COMPANY', style_font_red)
            worksheet.write(row, 1, tools.ustr(company_name), style_font_red2)
            row += 1
            worksheet.write(row, 0, 'TRANSACTION', style_font_red)
            worksheet.write(row, 1, tools.ustr(date_formate), style_font_red2_right)
            row += 1
            worksheet.write(row, 0, 'YEAR', style_font_red)
            worksheet.write(row, 1, tools.ustr(year), style_font_red2_right)
            row += 1
            worksheet.write(row, 0, 'PERIOD', style_font_red)
            worksheet.write(row, 1, tools.ustr(month), style_font_red2_right)
            row += 1
            worksheet.write(row, 0, 'DESCRIPTION', style_font_red)
            worksheet.write(row, 1, tools.ustr(month_year) + ' PROM WHS CPF SDF & FWL', style_font_red2)
            row += 1
            worksheet.write(row, 0, 'VAT COUNTRY', style_font_red)
            worksheet.write(row, 1, '', style_font_red2)
            row += 1
            worksheet.write(row, 0, 'VAT FLAG', style_font_red)
            worksheet.write(row, 1, '', style_font_red2)
            row += 1
            worksheet.write(row, 0, 'SAVED BACK?', style_font_red)
            worksheet.write(row, 1, 'no', style_font_red2)
            row += 1
            worksheet.write(row, 0, '', style_font_red)
            worksheet.write(row, 1, '', style_font_red2)
            worksheet.write(row, 2, '', style_font_red)
            worksheet.write(row, 3, '', style_font_red)
            worksheet.write(row, 4, 'EXCHANGE', style_font_red)
            worksheet.write(row, 5, '', style_font_red)
            worksheet.write(row, 6, 'VAT', style_font_red)
            worksheet.write(row, 7, 'VAT', style_font_red)
            worksheet.write(row, 8, 'VAT', style_font_red)
            worksheet.write(row, 9, '', style_font_red)
            worksheet.write(row, 10, '', style_font_red)
            worksheet.write(row, 11, '', style_font_red)
            worksheet.write(row, 12, 'ANALYSIS', style_font_red)
            row += 1
            worksheet.write(row, 0, 'GL CODE', style_font_red1)
            worksheet.write(row, 1, 'LINE DESCRIPTION', style_font_red3)
            worksheet.write(row, 2, 'CURRENCY', style_font_red1)
            worksheet.write(row, 3, 'AMOUNT', style_font_red1)
            worksheet.write(row, 4, 'RATE', style_font_red1)
            worksheet.write(row, 5, 'TOTAL', style_font_red1)
            worksheet.write(row, 6, 'TYPE', style_font_red1)
            worksheet.write(row, 7, 'CODE', style_font_red1)
            worksheet.write(row, 8, 'AMOUNT', style_font_red1)
            worksheet.write(row, 9, 'CC', style_font_red1)
            worksheet.write(row, 10, 'DEP', style_font_red1)
            worksheet.write(row, 11, 'JOB CODE', style_font_red1)
            worksheet.write(row, 12, 'CODE', style_font_red1)
            
            exchequer_ids = salary_report_for_exchequer_obj.search(cr, uid, [], order='name ASC')
            for exchequer in salary_report_for_exchequer_obj.browse(cr, uid, exchequer_ids):
                for categ in employee_category_obj.browse(cr, uid, emp_categ_ids):
                    salary_rule_ids = False
                    if Flag:
                        salary_rule_ids = hr_salary_rule_glcode_obj.search(cr, uid, [('salaryrule_id', '!=', False), ('gl_code_id', '=', exchequer.id), ('emp_categ_id', '=', categ.id), ('saved_back_salary', '=', True)])
                    else:
                        salary_rule_ids = hr_salary_rule_glcode_obj.search(cr, uid, [('salaryrule_id', '!=', False), ('gl_code_id', '=', exchequer.id), ('emp_categ_id', '=', categ.id), ('saved_back_cpf', '=', True)])
                    for emp in categ.employee_ids:
                        payslip_ids = payslip_obj.search(cr, uid, [('employee_id','=',emp.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'done', 'verify'])])
                        if not payslip_ids:
                            continue
                        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                            rule_name = ''
                            for salary_rule in hr_salary_rule_glcode_obj.browse(cr, uid, salary_rule_ids):
                                print_flag = False
                                if salary_rule.apply_bank_cheque == 'apply_for_bank' and not payslip.employee_id.bank_detail_ids:
                                    print_flag = True
                                elif salary_rule.apply_bank_cheque == 'apply_for_cheque' and payslip.employee_id.bank_detail_ids:
                                    print_flag = True
                                if print_flag:
                                    continue
                                amount = 0.0
                                rule_name = tools.ustr(salary_rule.salaryrule_id.name)
                                for line in payslip.line_ids:
                                    if line.code == salary_rule.salaryrule_id.code:
                                        if salary_rule.nagative:
                                            amount = line.amount * -1
                                        else:
                                            amount = line.amount
                                        break
                                if not amount:
                                    continue
                                total_amount += amount
                                cost_center_list = []
                                user_login = ""
                                if payslip.employee_id and payslip.employee_id.user_id.id:
                                    sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_id.date_order', '<=', final_last_day_of_pre_month),
                                                                                               ('order_id.date_order', '>=', final_first_day_of_pre_month),
                                                                                               ('order_id.user_id', '=', payslip.employee_id.user_id.id),
                                                                                               ('order_id.is_sale_order', '=', False),
                                                                                               ('order_id.state', '=', 'done')])
                                    user_login += "xxx" + payslip.employee_id.user_id.login + "xxx"
                                    if sale_order_line_ids:
                                        for order in sale_order_line_obj.browse(cr, uid, sale_order_line_ids):
                                            if order and order.product_id and order.product_id.categ_id and order.product_id.categ_id.cost_center_id:
                                                if order.product_id.categ_id.cost_center_id.name not in cost_center_list:
                                                    cost_center_list.append(order.product_id.categ_id.cost_center_id.name)
                                cost_center_length = len(cost_center_list)
                                if cost_center_list and cost_center_length:
                                    cost_center_amount = amount / cost_center_length
                                    for cost_center in cost_center_list:
                                        row += 1
                                        worksheet.write(row, 0, tools.ustr(exchequer.name), left_blue)
                                        worksheet.write(row, 1, tools.ustr(month_year) + ' ' + tools.ustr(categ.name) + ' ' + rule_name + ' ' + user_login, header2)
                                        worksheet.write(row, 2, tools.ustr(currency_symbol), header_center)
                                        worksheet.write(row, 3, round(cost_center_amount or 0.00, 2), header)
                                        worksheet.write(row, 4, '1', header_center)
                                        worksheet.write(row, 5, round(cost_center_amount or 0.00, 2), header)
                                        worksheet.write(row, 6, 'N/A', header)
                                        worksheet.write(row, 7, '', header)
                                        worksheet.write(row, 8, '', header)
                                        worksheet.write(row, 9, tools.ustr(cost_center), header_center)
                                        worksheet.write(row, 10, 'GEN', header_center)
                                        worksheet.write(row, 11, '', header)
                                else:
                                    row += 1
                                    worksheet.write(row, 0, tools.ustr(exchequer.name), left_blue)
                                    worksheet.write(row, 1, tools.ustr(month_year) + ' ' + tools.ustr(categ.name) + ' ' + rule_name + ' ' + user_login, header2)
                                    worksheet.write(row, 2, tools.ustr(currency_symbol), header_center)
                                    worksheet.write(row, 3, round(amount or 0.00, 2), header)
                                    worksheet.write(row, 4, '1', header_center)
                                    worksheet.write(row, 5, round(amount or 0.00, 2), header)
                                    worksheet.write(row, 6, 'N/A', header)
                                    worksheet.write(row, 7, '', header)
                                    worksheet.write(row, 8, '', header)
                                    worksheet.write(row, 9, '', header_center)
                                    worksheet.write(row, 10, 'GEN', header_center)
                                    worksheet.write(row, 11, '', header)

            for exchequer in salary_report_for_exchequer_obj.browse(cr, uid, exchequer_ids):
                for categ in employee_category_obj.browse(cr, uid, emp_categ_ids):
                    cost_center_list = []
                    register_name = ''
                    register_amount = 0.0
                    salary_rule_ids = False
                    if Flag:
                        salary_rule_ids = hr_salary_rule_glcode_obj.search(cr, uid, [('register_id', '!=', False), ('gl_code_id', '=', exchequer.id), ('emp_categ_id', '=', categ.id), ('saved_back_salary', '=', True)])
                    else:
                        salary_rule_ids = hr_salary_rule_glcode_obj.search(cr, uid, [('register_id', '!=', False), ('gl_code_id', '=', exchequer.id), ('emp_categ_id', '=', categ.id), ('saved_back_cpf', '=', True)])
                    for emp in categ.employee_ids:
                        payslip_ids = payslip_obj.search(cr, uid, [('employee_id','=',emp.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'done', 'verify'])])
                        if not payslip_ids:
                            continue
                        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                            for salary_rule in hr_salary_rule_glcode_obj.browse(cr, uid, salary_rule_ids):
                                print_flag = False
                                if salary_rule.apply_bank_cheque == 'apply_for_bank' and not payslip.employee_id.bank_detail_ids:
                                    print_flag = True
                                elif salary_rule.apply_bank_cheque == 'apply_for_cheque' and payslip.employee_id.bank_detail_ids:
                                    print_flag = True
                                if print_flag:
                                    continue
                                amount = 0.0
                                if not register_name:
                                    register_name = tools.ustr(salary_rule.register_id.name)
                                for line in payslip.line_ids:
                                    if line.salary_rule_id.register_id.id == salary_rule.register_id.id:
                                        if salary_rule.nagative:
                                            amount += line.amount * -1
                                        else:
                                            amount += line.amount
                                if not amount:
                                    continue
                                total_amount += amount
                                register_amount += amount
                                if payslip.employee_id and payslip.employee_id.user_id.id:
                                    sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_id.date_order', '<=', final_last_day_of_pre_month),
                                                                                               ('order_id.date_order', '>=', final_first_day_of_pre_month),
                                                                                               ('order_id.user_id', '=', payslip.employee_id.user_id.id),
                                                                                               ('order_id.is_sale_order', '=', False),
                                                                                               ('order_id.state', '=', 'done')])
                                    if sale_order_line_ids:
                                        for order in sale_order_line_obj.browse(cr, uid, sale_order_line_ids):
                                            if order and order.product_id and order.product_id.categ_id and order.product_id.categ_id.cost_center_id:
                                                if order.product_id.categ_id.cost_center_id.name not in cost_center_list:
                                                    cost_center_list.append(order.product_id.categ_id.cost_center_id.name)
                    if not register_amount:
                        continue
                    cost_center_length = len(cost_center_list)
                    if cost_center_list and cost_center_length:
                        cost_center_amount = register_amount / cost_center_length
                        for cost_center in cost_center_list:
                            row += 1
                            worksheet.write(row, 0, tools.ustr(exchequer.name), left_blue)
                            worksheet.write(row, 1,  tools.ustr(month_year) + ' ' + tools.ustr(categ.name) + ' ' + register_name, header2)
                            worksheet.write(row, 2, tools.ustr(currency_symbol), header_center)
                            worksheet.write(row, 3, round(cost_center_amount or 0.00, 2), header)
                            worksheet.write(row, 4, '1', header_center)
                            worksheet.write(row, 5, round(cost_center_amount or 0.00, 2), header)
                            worksheet.write(row, 6, 'N/A', header)
                            worksheet.write(row, 7, '', header)
                            worksheet.write(row, 8, '', header)
                            worksheet.write(row, 9, tools.ustr(cost_center), header_center)
                            worksheet.write(row, 10, 'GEN', header_center)
                            worksheet.write(row, 11, '', header)
                    else:
                        row += 1
                        worksheet.write(row, 0, tools.ustr(exchequer.name), left_blue)
                        worksheet.write(row, 1,  tools.ustr(month_year) + ' ' + tools.ustr(categ.name) + ' ' + register_name, header2)
                        worksheet.write(row, 2, tools.ustr(currency_symbol), header_center)
                        worksheet.write(row, 3, round(register_amount or 0.00, 2), header)
                        worksheet.write(row, 4, '1', header_center)
                        worksheet.write(row, 5, round(register_amount or 0.00, 2), header)
                        worksheet.write(row, 6, 'N/A', header)
                        worksheet.write(row, 7, '', header)
                        worksheet.write(row, 8, '', header)
                        worksheet.write(row, 9, '', header_center)
                        worksheet.write(row, 10, 'GEN', header_center)
                        worksheet.write(row, 11, '', header)
            
            
            row += 1
#            worksheet.write(row, 0, '', left_blue)
#            worksheet.write(row, 1, '', header2)
#            worksheet.write(row, 12, '', right_blue)
#            row += 1
#            worksheet.write(row, 1, '', header2)
#            worksheet.write(row, 12, '', right_blue)
#            row += 1
#            worksheet.write(row, 1, '', header2)
#            worksheet.write(row, 12, '', right_blue)
#            row += 1
#            worksheet.write(row, 0, '', bottom_blue)
#            worksheet.write(row, 1, 'CHECKING', bottom_blue1)
#            worksheet.write(row, 2, '', bottom_blue)
#            worksheet.write(row, 3, round(total_amount or 0.00, 2), bottom_blue)
#            worksheet.write(row, 4, '', bottom_blue)
#            worksheet.write(row, 5, round(total_amount or 0.00, 2), bottom_blue)
#            worksheet.write(row, 6, '', bottom_blue)
#            worksheet.write(row, 7, '', bottom_blue)
#            worksheet.write(row, 8, '', bottom_blue)
#            worksheet.write(row, 9, '', bottom_blue)
#            worksheet.write(row, 10, '', bottom_blue)
#            worksheet.write(row, 11, '', bottom_blue)
#            worksheet.write(row, 12, '', bottom_right_blue)
            Flag = True
        
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)


    _columns = {
        "file":fields.binary("Click On Save As Button To Download File", readonly=True),
        "name":fields.char("Name" , size=32, readonly=True, invisible=True)
    }

    def _get_file_name(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        period_id = context.get('period_from')
        if not period_id:
            return 'Exchequer.xls'
        period_data = period_obj.browse(cr, uid, period_id[0], context=context)
        end_date = datetime.datetime.strptime(period_data.date_stop, DEFAULT_SERVER_DATE_FORMAT)
        monthyear = end_date.strftime('%b%Y')
        file_name = 'Exchequer ' + monthyear + '.xls'
        return file_name

    _defaults = {
        'name': _get_file_name,
        'file': _get_payroll_exchequer_report_data
    }

export_payroll_exchequer_report()

class payroll_exchequer_report(osv.osv_memory):

    _name = 'payroll.exchequer.report'

    _columns = {
            'period_from': fields.many2one('account.period', 'Period From')
    }

    def export_payroll_exchequer_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        context.update({'period_from': data['period_from']})
        return {
            'name': _('Binary'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'export.payroll.exchequer.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

payroll_exchequer_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
