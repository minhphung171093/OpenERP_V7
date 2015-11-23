# -*- encoding: utf-8 -*-

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

class pr_wh_payroll_summary(osv.osv_memory):

    _name = 'pr.wh.payroll.summary'

    def _get_pr_wh_payroll_report_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        workbook = xlwt.Workbook()
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 180')
        header2 = xlwt.easyxf('font: bold off, height 150; align: wrap on;')
        header3 = xlwt.easyxf('font: bold 1, height 150; align: wrap off;')
        border_style = xlwt.easyxf('pattern: pattern solid, fore_colour white; borders: left double, right double, top double, bottom double, bottom_color black; font: bold on, height 150, color black; align: wrap off')
        style_font_red = xlwt.easyxf('font: name Arial, bold on, color black, height 150; align: wrap on;')
        promo_header_bold = xlwt.easyxf('font: bold on, height 180; align: wrap off; borders: left double, right double, top double, bottom double, right_color black, left_color black, top_color black, bottom_color black;')
        promo_header_bold_off = xlwt.easyxf('font: bold off, height 150; align: wrap off; borders: left double, right double, top double, bottom double, right_color black, left_color black, top_color black, bottom_color black;')
        
        header.num_format_str = '0.00'
        header2.num_format_str = '0.00'
        border_style.num_format_str = '0.00'
        style_font_red.num_format_str = '0.00'
        
        promo_header_bold.num_format_str = '0.00'
        promo_header_bold_off.num_format_str = '0.00'
        
        period_obj = self.pool.get('account.period')
        product_category_obj = self.pool.get('product.category')
        hr_employee_category = self.pool.get('hr.employee.category')
        sale_order_obj = self.pool.get('sale.order')
        sale_order_line_obj = self.pool.get('sale.order.line')
        payslip_obj = self.pool.get('hr.payslip')
        res_company_obj = self.pool.get('res.company')
        
        company_id = res_company_obj.search(cr, uid, [])
        company_name = ''
        if company_id:
            company_name = res_company_obj.browse(cr, uid, company_id[0]).name
        
        date_from = period_obj.browse(cr, uid, context.get('period_from')[0]).date_start
        date_to = period_obj.browse(cr, uid, context.get('period_from')[0]).date_stop
        month_year = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%B %Y')
        
        date_from1 = datetime.datetime.strptime(str(date_from), DEFAULT_SERVER_DATE_FORMAT)
        previous_month_obj = parser.parse(date_from1.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
        total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
        first_day_of_previous_month = datetime.datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
        last_day_of_previous_month = datetime.datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
        final_first_day_of_pre_month = datetime.datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        final_last_day_of_pre_month = datetime.datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        
        category_ids = hr_employee_category.search(cr, uid, [('name', 'in', ['BAFT', 'BAPT'])])
        product_categ_ids = product_category_obj.search(cr, uid, [('parent_id', '=', False)])
        
        for category in hr_employee_category.browse(cr, uid, category_ids):
            worksheet = workbook.add_sheet(category.name)
            row = 2
            worksheet.col(0).width = 1500
            worksheet.col(1).width = 8000
            worksheet.write(row, 1, 'Month : ' + tools.ustr(month_year), header)
            row += 1
            worksheet.write(row, 1, 'PPD - PROMOTERS PAYROLL (FULL TIMER)', header)
            row += 1
            
            if product_categ_ids:
                col = 3
                prod_cat_sq_no = 1
                prod_cat_row_no = row
                worksheet.write(prod_cat_row_no, 1, 'STAFF', header)
                row += 1
                worksheet.row(row).height = 500
                prod_categ_list = []
                worksheet.write(row, 2, 'TOTAL', header)
                for categ in product_category_obj.browse(cr, uid, product_categ_ids):
                    worksheet.write(prod_cat_row_no, col, prod_cat_sq_no, header3)
                    worksheet.write(row, col, tools.ustr(categ.name), style_font_red)
                    prod_cat_sq_no += 1
                    col += 1
                    prod_categ_list.append(categ.name)
                    worksheet.col(col).width = 3200
            
            sq_no = 1
            employee_list = []
            total_categ_dict = {}
            total_emp_sale_tot = 0.00
            for employee in category.employee_ids:
                emp_dict = {}
                emp_pro_cat_amt_list = []
                total_emp_sale = 0.001
                row += 1
                sale_order_user_ids = []
                if employee and employee.user_id:
                    cr.execute("""select id from sale_order
                            where date_order <= %s and date_order >= %s and user_id = %s
                            and is_sale_order = False and state = 'done' """, (final_last_day_of_pre_month, final_first_day_of_pre_month, employee.user_id.id)) 
                    res_total = cr.fetchall()
                    if res_total:
                        for res in res_total:
                            if res and res[0]:
                                sale_order_user_ids.append(res[0])
                    if sale_order_user_ids:
                        cr.execute("select sum(amount_total) from sale_order where id in %s" , (tuple(sale_order_user_ids),))
                        res_total_sale = cr.fetchall()
                        if res_total_sale and res_total_sale[0] and res_total_sale[0][0]:
                            total_emp_sale = res_total_sale[0][0]
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, tools.ustr(employee.name), border_style)
                worksheet.write(row, 2, total_emp_sale, header2)
                sq_no += 1
                col_pro_cat = 3
                for categ in product_category_obj.browse(cr, uid, product_categ_ids):
                    child_ids = product_category_obj.search(cr, uid, [('id', 'child_of', [categ.id])])
                    categ_amt_sale = 0.00
                    if employee and employee.user_id:
                        sale_order_line_ids = []
                        if sale_order_user_ids:
                            cr.execute("""select id from sale_order_line
                                    where order_id in %s and product_id in (select id from product_product where product_tmpl_id in 
                                (select id from product_template where categ_id in %s ))""" , (tuple(sale_order_user_ids), tuple(child_ids) ))
                        res_sale_order = cr.fetchall()
                        if res_sale_order:
                            for res in res_sale_order:
                                if res and res[0]:
                                    sale_order_line_ids.append(res[0])
                        if sale_order_line_ids:
                            cr.execute("select sum(price_unit*product_uom_qty) from sale_order_line where id in %s" , (tuple(sale_order_line_ids),))
                            res_total_sale = cr.fetchall()
                            if res_total_sale and res_total_sale[0] and res_total_sale[0][0]:
                                categ_amt_sale = res_total_sale[0][0]
                    worksheet.write(row, col_pro_cat, categ_amt_sale, header2)
                    col_pro_cat += 1
                    emp_pro_cat_amt_list.append(categ_amt_sale)
                    
                    if total_categ_dict.has_key(categ.id):
                        total_categ_dict[categ.id] = total_categ_dict[categ.id] + categ_amt_sale
                    else:
                        total_categ_dict.update({
                                categ.id: categ_amt_sale,
                        })
                total_emp_sale_tot += total_emp_sale
                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', employee.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                emp_dict = {'payslip_ids': payslip_ids, 'emp_id': employee.id, 'employee_name': employee.name, 'total_sale_amt': total_emp_sale, 'cat_amt_list': emp_pro_cat_amt_list}
                employee_list.append(emp_dict)

            row += 1
            col = 3
            worksheet.write(row, 2, total_emp_sale_tot, header)
            for categ_prod in product_category_obj.browse(cr, uid, product_categ_ids):
                for categ in total_categ_dict:
                    if categ == categ_prod.id:
                        worksheet.write(row, col, total_categ_dict.get(categ), header)
                        col += 1
            
            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'TOTAL', header)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            for emp in employee_list:
                emp_per = 0.00
                emp_tot_amt = 0.001
                if emp.get('total_sale_amt'):
                    emp_per = 100.00
                    emp_tot_amt = emp.get('total_sale_amt')
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, tools.ustr(emp_per) + '%', header2)
                col_prod_cat_amt = 3
                for cat_per in emp.get('cat_amt_list'):
                    worksheet.write(row, col_prod_cat_amt, tools.ustr(round((cat_per / emp_tot_amt) * 100 or 0.00, 2)) + '%', header2)
                    col_prod_cat_amt += 1
                sq_no += 1
                row += 1

            row += 2
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'ACTUAL SALARY', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            salary_list = []
            cat_per_no = 0
            basic_amt_total = 0.00
            for emp in employee_list:
                basic_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, emp.get('payslip_ids')):
                        basic_amt += payslip.contract_id and payslip.contract_id.wage_to_pay or 0.00
#                        for line in payslip.line_ids:
#                            if line.category_id.code == 'BASIC':
#                                basic_amt += line.amount
                basic_amt_total += basic_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, basic_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    salaryamount = (basic_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((basic_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if salary_list and cat_per_no > 0:
                        totamt = salary_list[i] + salaryamount
                        salary_list[i] = totamt
                    else:
                        salary_list.append(salaryamount)
                    col_prod_cat_amt += 1
                    i += 1
                cat_per_no += 1
                sq_no += 1 
                row += 1
            worksheet.write(row, 2, basic_amt_total, header)
            col = 3
            for salary in salary_list:
                worksheet.write(row, col, salary, header)
                col += 1

            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'OVERTIME', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            overtime_list = []
            cat_perovertime_no = 0
            overtime_amt_total = 0.00
            for emp in employee_list:
                overtime_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, [emp.get('payslip_ids')[0]]):
                        for line in payslip.line_ids:
                            if line.code in ['SC100', 'SC102', 'SC203']:
                                overtime_amt += line.amount
                            elif line.code in ['SC206', 'SC207']:
                                overtime_amt = overtime_amt - line.amount
                overtime_amt_total += overtime_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, overtime_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    overtimeamount = (overtime_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((overtime_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if overtime_list and cat_perovertime_no > 0:
                        totamt = overtime_list[i] + overtimeamount
                        overtime_list[i] = totamt
                    else:
                        overtime_list.append(overtimeamount)
                    i += 1
                    col_prod_cat_amt += 1
                cat_perovertime_no += 1
                sq_no += 1
                row += 1
            worksheet.write(row, 2, overtime_amt_total, header)
            col = 3
            for overtime in overtime_list:
                worksheet.write(row, col, overtime, header)
                col += 1


            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'ALLOWANCE', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            allowance_list = []
            cat_perallowance_no = 0
            allowance_amt_total = 0.00
            for emp in employee_list:
                allowance_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, [emp.get('payslip_ids')[0]]):
                        for line in payslip.line_ids:
                            if line.code in ['SC106', 'SC108', 'SC123']:
                                allowance_amt += line.amount
                allowance_amt_total += allowance_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, allowance_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    allowanceamount = (allowance_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((allowance_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if allowance_list and cat_perallowance_no > 0:
                        totamt = allowance_list[i] + allowanceamount
                        allowance_list[i] = totamt
                    else:
                        allowance_list.append(allowanceamount)
                    i += 1
                    col_prod_cat_amt += 1
                cat_perallowance_no += 1
                sq_no += 1
                row += 1
            worksheet.write(row, 2, allowance_amt_total, header)
            col = 3
            for allowance in allowance_list:
                worksheet.write(row, col, allowance, header)
                col += 1


            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'SUPERVISORY/MANAGERIAL', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            supervisory_list = []
            cat_persupervisory_no = 0
            supervisory_amt_total = 0.00
            for emp in employee_list:
                supervisor_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, [emp.get('payslip_ids')[0]]):
                        for line in payslip.line_ids:
                            if line.code == 'SC108':
                                supervisor_amt += line.amount
                supervisory_amt_total += supervisor_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, supervisor_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    supervisoryamount = (supervisor_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((supervisor_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if supervisory_list and cat_persupervisory_no > 0:
                        totamt = supervisory_list[i] + supervisoryamount
                        supervisory_list[i] = totamt
                    else:
                        supervisory_list.append(supervisoryamount)
                    i += 1
                    col_prod_cat_amt += 1
                cat_persupervisory_no += 1
                sq_no += 1
                row += 1
            worksheet.write(row, 2, supervisory_amt_total, header)
            col = 3
            for supervisory in supervisory_list:
                worksheet.write(row, col, supervisory, header)
                col += 1


            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'COMMISSION', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            commission_list = []
            cat_percommission_no = 0
            commission_amt_total = 0.00
            for emp in employee_list:
                commission_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, [emp.get('payslip_ids')[0]]):
                        for line in payslip.line_ids:
                            if line.code == 'SC104':
                                commission_amt += line.amount
                commission_amt_total += commission_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, commission_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    commissionamount = (commission_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((commission_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if commission_list and cat_percommission_no > 0:
                        totamt = commission_list[i] + commissionamount
                        commission_list[i] = totamt
                    else:
                        commission_list.append(commissionamount)
                    i += 1
                    col_prod_cat_amt += 1
                cat_percommission_no += 1
                sq_no += 1
                row += 1
            worksheet.write(row, 2, commission_amt_total, header)
            col = 3
            for commission in commission_list:
                worksheet.write(row, col, commission, header)
                col += 1


            row += 3
            worksheet.row(row).height = 500
            worksheet.write(row, 2, 'INCENTIVE', style_font_red)
            col_pro_cat = 3
            for prod_categ in prod_categ_list:
                worksheet.write(row, col_pro_cat, prod_categ, style_font_red)
                col_pro_cat += 1
            row += 1
            sq_no = 1
            incentive_list = []
            cat_perincentive_no = 0
            incentive_amt_total = 0.00
            for emp in employee_list:
                incentive_amt = 0.001
#                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.get('emp_id')), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if emp.get('payslip_ids'):
                    for payslip in payslip_obj.browse(cr, uid, [emp.get('payslip_ids')[0]]):
                        for line in payslip.line_ids:
                            if line.code == 'SC105':
                                incentive_amt += line.amount
                incentive_amt_total += incentive_amt
                worksheet.write(row, 0, sq_no, header3)
                worksheet.write(row, 1, emp.get('employee_name'), border_style)
                worksheet.write(row, 2, incentive_amt, header2)
                col_prod_cat_amt = 3
                i = 0
                for cat_per in emp.get('cat_amt_list'):
                    incentiveamount = (incentive_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100)
                    worksheet.write(row, col_prod_cat_amt, round((incentive_amt * ((cat_per / emp.get('total_sale_amt') or 0.00) * 100) / 100) or 0.00, 2), header2)
                    totamt = 0.00
                    if incentive_list and cat_perincentive_no > 0:
                        totamt = incentive_list[i] + incentiveamount
                        incentive_list[i] = totamt
                    else:
                        incentive_list.append(incentiveamount)
                    i += 1
                    col_prod_cat_amt += 1
                cat_perincentive_no += 1
                sq_no += 1
                row += 1
            worksheet.write(row, 2, incentive_amt_total, header)
            col = 3
            for incentive in incentive_list:
                worksheet.write(row, col, incentive, header)
                col += 1
        
        
        
        
        prom_pay_worksheet = workbook.add_sheet('PROMOTORS PAYROLL SCHED')
        prom_cpf_worksheet = workbook.add_sheet('PROM CPF SDF FWL')
        
        prom_pay_worksheet.col(0).width = 1500
        prom_pay_worksheet.col(1).width = 9000
        prom_pay_worksheet.col(2).width = 3500
        prom_pay_worksheet.col(3).width = 3500
        prom_pay_worksheet.col(4).width = 4500
        prom_pay_worksheet.col(5).width = 4500
        prom_pay_worksheet.col(6).width = 4500
        prom_pay_worksheet.col(7).width = 4500
        prom_pay_worksheet.col(8).width = 4500
        prom_pay_worksheet.col(9).width = 4500
        prom_pay_worksheet.col(10).width = 4500
        prom_pay_worksheet.col(11).width = 4500
        prom_pay_worksheet.col(12).width = 4500
        prom_pay_worksheet.col(13).width = 4500
        
        prom_cpf_worksheet.col(0).width = 1500
        prom_cpf_worksheet.col(1).width = 9000
        prom_cpf_worksheet.col(2).width = 3500
        prom_cpf_worksheet.col(3).width = 3500
        prom_cpf_worksheet.col(4).width = 4500
        prom_cpf_worksheet.col(5).width = 4500
        prom_cpf_worksheet.col(6).width = 4500
        prom_cpf_worksheet.col(7).width = 4500
        prom_cpf_worksheet.col(8).width = 4500
        
        prom_pay_row = 4
        prom_cpf_row = 4
        prom_pay_worksheet.write(prom_pay_row, 3, tools.ustr(company_name), header)
        prom_cpf_worksheet.write(prom_pay_row, 3, tools.ustr(company_name), header)
        prom_pay_row += 1
        prom_cpf_row += 1
        prom_pay_worksheet.write(prom_pay_row, 3, 'PROMOTERS & WAREHOUSE PAYROLL FOR THE MONTH ENDED ' + ' ' + tools.ustr(month_year or ''), header)
        prom_cpf_worksheet.write(prom_pay_row, 3, 'PROMOTERS & WAREHOUSE PAYROLL FOR THE MONTH ' + ' ' + tools.ustr(month_year or ''), header)
        prom_pay_row += 2
        prom_cpf_row += 2
        prom_pay_worksheet.write(prom_pay_row, 4, 'SALARY', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 5, 'OVERTIME', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 6, 'ALLOWANCE', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 7, 'SUP/MGR ALLOW', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 8, 'COMMISSION', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 9, 'INCENTIVE', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 10, 'BONUS', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 11, 'TOTAL', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 12, 'Employer CPF', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 13, 'NET PAY', promo_header_bold)
        
        prom_cpf_worksheet.write(prom_cpf_row, 4, 'EE CPF', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 5, 'ER CPF', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 6, 'SDF', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 7, 'FWL', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 8, 'TOTAL', promo_header_bold)
        
        prom_pay_row += 1
        prom_pay_worksheet.write(prom_pay_row, 2, 'DEP', header2)
        prom_pay_worksheet.write(prom_pay_row, 3, 'CC', promo_header_bold)
        
        prom_cpf_row += 1
        prom_cpf_worksheet.write(prom_cpf_row, 2, 'DEP', header2)
        prom_cpf_worksheet.write(prom_cpf_row, 3, 'CC', promo_header_bold)
        
        tot_cpfsdf_amt = tot_cpfee_amt = tot_cpfer_amt = tot_fwl_amt = tot_basic_salary = tot_overtime_amt = tot_net_amt = tot_supmgr_amt = tot_cpf_amt = tot_gross_amt = tot_bonus_amt = tot_incentive_amt = tot_commission_amt = tot_allowance_amt = 0.00
        
        new_category_ids = hr_employee_category.search(cr, uid, [('name', 'in', ['FCFT', 'BAFT', 'FCPT', 'BAPT','WH-D','WH-G','PBP'])])
        for category in hr_employee_category.browse(cr, uid, new_category_ids):
            cpfsdf_amt = cpfee_amt = cpfer_amt = fwl_amt = basic_salary = overtime_amt = net_amt = supmgr_amt = cpf_amt = gross_amt = bonus_amt = incentive_amt = commission_amt = allowance_amt = 0.00
            for employee in category.employee_ids:
                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', employee.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                if payslip_ids:
                    for line in payslip_obj.browse(cr, uid, payslip_ids[0]).line_ids:
                        if line.code == 'BASIC':
                            basic_salary += line.amount
                        if line.code == 'SC102':
                            overtime_amt += line.amount
                        if line.code in ['SC106', 'SC108', 'SC123']:
                            allowance_amt += line.amount
                        if line.code == 'SC104':
                            commission_amt += line.amount
                        if line.code == 'SC105':
                            incentive_amt += line.amount
                        if line.code == 'SC121':
                            bonus_amt += line.amount
                        if line.code == 'GROSS':
                            gross_amt += line.amount
                        if line.code == 'CPFEE' or line.category_id.code == 'CAT_CPF_EMPLOYEE':
                            cpf_amt += line.amount
                        if line.code == 'NET':
                            net_amt += line.amount
                        if line.code == 'SC108':
                            supmgr_amt += line.amount
                        
                        if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                            cpfee_amt += line.amount
                        if line.category_id.code == 'CAT_CPF_EMPLOYER':
                            cpfer_amt += line.amount
                        if line.category_id.code == 'CATCPFAGENCYSERVICESER':
                            fwl_amt += line.amount
                        if line.code == 'CPFSDL':
                            cpfsdf_amt += line.amount
            tot_basic_salary += basic_salary
            tot_overtime_amt += overtime_amt
            tot_net_amt += net_amt
            tot_cpf_amt += cpf_amt
            tot_gross_amt += gross_amt
            tot_bonus_amt += bonus_amt
            tot_incentive_amt += incentive_amt
            tot_commission_amt += commission_amt
            tot_allowance_amt += allowance_amt
            tot_supmgr_amt += supmgr_amt
            
            tot_cpfee_amt += cpfee_amt
            tot_cpfer_amt += cpfer_amt
            tot_fwl_amt += fwl_amt
            tot_cpfsdf_amt += cpfsdf_amt
            
            prom_pay_row += 1
            prom_pay_worksheet.write(prom_pay_row, 3, tools.ustr(category.name or ''), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 4, round(basic_salary or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 5, round(overtime_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 6, round(allowance_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 7, round(supmgr_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 8, round(commission_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 9, round(incentive_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 10, round(bonus_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 11, round(gross_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 12, round(cpf_amt or 0.00, 2), promo_header_bold_off)
            prom_pay_worksheet.write(prom_pay_row, 13, round(net_amt or 0.00, 2), promo_header_bold_off)
            
            prom_cpf_row += 1
            prom_cpf_worksheet.write(prom_cpf_row, 3, tools.ustr(category.name or ''), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 4, round(cpfee_amt or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 5, round(cpfer_amt or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 6, round(cpfsdf_amt or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 7, round(fwl_amt or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 8, round(net_amt or 0.00, 2), promo_header_bold)
        prom_pay_row += 2
        prom_pay_worksheet.write(prom_pay_row, 3, 'TOTAL', promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 4, round(tot_basic_salary or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 5, round(tot_overtime_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 6, round(tot_allowance_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 7, round(tot_supmgr_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 8, round(tot_commission_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 9, round(tot_incentive_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 10, round(tot_bonus_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 11, round(tot_gross_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 12, round(tot_cpf_amt or 0.00, 2), promo_header_bold_off)
        prom_pay_worksheet.write(prom_pay_row, 13, round(tot_net_amt or 0.00, 2), promo_header_bold_off)
        
        prom_cpf_row += 2
        prom_cpf_worksheet.write(prom_cpf_row, 3, 'TOTAL', promo_header_bold_off)
        prom_cpf_worksheet.write(prom_cpf_row, 4, round(tot_cpfee_amt or 0.00, 2), promo_header_bold_off)
        prom_cpf_worksheet.write(prom_cpf_row, 5, round(tot_cpfer_amt or 0.00, 2), promo_header_bold_off)
        prom_cpf_worksheet.write(prom_cpf_row, 6, round(tot_cpfsdf_amt or 0.00, 2), promo_header_bold_off)
        prom_cpf_worksheet.write(prom_cpf_row, 7, round(tot_fwl_amt or 0.00, 2), promo_header_bold_off)
        prom_cpf_worksheet.write(prom_cpf_row, 8, round(tot_net_amt or 0.00, 2), promo_header_bold_off)
        
        prom_pay_row += 2
        prom_cpf_row += 2
        grand_tot_emp_cpfsdl_amt_categ = grand_tot_emp_gross_amt = grand_tot_emp_fwl_amt_categ = grand_tot_emp_cpfee_amt_categ = grand_tot_emp_cpfer_amt_categ = grand_tot_emp_cpf_amt = grand_tot_emp_supmgr_amt = grand_tot_emp_bonus_amt = grand_tot_emp_incentive_amt = grand_tot_emp_net_amt = grand_tot_emp_commission_amt = grand_tot_emp_allowance_amt = grand_tot_emp_overtime_amt = grand_tot_emp_basic_salary_amt = 0.00
        for category in hr_employee_category.browse(cr, uid, new_category_ids):
            tot_emp_cpfsdl_amt_categ = tot_emp_cpfee_amt_categ = tot_emp_cpfer_amt_categ = tot_emp_fwl_amt_categ = tot_emp_basic_salary_amt = tot_emp_overtime_amt = tot_emp_allowance_amt = tot_emp_commission_amt = tot_emp_net_amt = tot_emp_incentive_amt = tot_emp_gross_amt = tot_emp_bonus_amt = tot_emp_cpf_amt = tot_emp_supmgr_amt = 0.00
            prom_pay_row += 1
            prom_pay_worksheet.write(prom_pay_row, 1, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 2, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 3, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 4, 'SALARY', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 5, 'OVERTIME', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 6, 'ALLOWANCE', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 7, 'SUP/MGR ALLOW', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 8, 'COMMISSION', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 9, 'INCENTIVE', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 10, 'BONUS', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 11, 'TOTAL', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 12, 'Employer CPF', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 13, 'NET PAY', promo_header_bold)
            
            prom_cpf_row += 1
            prom_cpf_worksheet.write(prom_cpf_row, 1, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 2, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 3, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 4, 'EE CPF', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 5, 'ER CPF', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 6, 'SDF', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 7, 'FWL', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 8, 'TOTAL', promo_header_bold)
            
            prom_pay_row += 1
            prom_pay_worksheet.write(prom_pay_row, 1, tools.ustr(category.name or ''), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 2, 'DEPT', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 3, 'CC', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 4, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 5, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 6, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 7, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 8, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 9, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 10, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 11, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 12, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 13, '', promo_header_bold)
            
            prom_cpf_row += 1
            prom_cpf_worksheet.write(prom_cpf_row, 1, tools.ustr(category.name or ''), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 2, 'DEPT', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 3, 'CC', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 4, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 5, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 6, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 7, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 8, '', promo_header_bold)
            categ_no = 1
            for categ in product_category_obj.browse(cr, uid, product_categ_ids):
                child_ids = product_category_obj.search(cr, uid, [('id', 'child_of', [categ.id])])
                cost_center_list = []
                emp_cpfsdl_amt_categ = emp_fwl_amt_categ = emp_cpfer_amt_categ = emp_cpfee_amt_categ = emp_basic_salary_amt = emp_overtime_amt = emp_allowance_amt = emp_commission_amt = emp_net_amt = emp_supmgr_amt = emp_incentive_amt = emp_gross_amt = emp_bonus_amt = emp_cpf_amt = 0.00
                for employee in category.employee_ids:
                    total_amt_sale = 0.00
                    if employee and employee.user_id:
                        sale_order_user_ids = []
                        cr.execute("""select id from sale_order
                            where date_order <= %s and date_order >= %s and user_id = %s
                            and is_sale_order = False and state = 'done' """, (final_last_day_of_pre_month, final_first_day_of_pre_month, employee.user_id.id)) 
                        res_total = cr.fetchall()
                        if res_total:
                            for res in res_total:
                                if res and res[0]:
                                    sale_order_user_ids.append(res[0])
                        if sale_order_user_ids:
                            cr.execute("select sum(price_unit*product_uom_qty) from sale_order_line where order_id in %s" , (tuple(sale_order_user_ids),))
                            res_total_sale = cr.fetchall()
                            if res_total_sale and res_total_sale[0] and res_total_sale[0][0]:
                                total_amt_sale = res_total_sale[0][0]
                        categ_amt_sale = 0.00
                        sale_order_line_ids = []
                        if sale_order_user_ids:
                            cr.execute("""select id from sale_order_line
                                    where order_id in %s and product_id in (select id from product_product where product_tmpl_id in 
                                (select id from product_template where categ_id in %s ))""" , (tuple(sale_order_user_ids), tuple(child_ids) ))
                        res_sale_order = cr.fetchall()
                        if res_sale_order:
                            for res in res_sale_order:
                                if res and res[0]:
                                    sale_order_line_ids.append(res[0])
                        
                        if sale_order_line_ids:
                            cr.execute("select sum(price_unit*product_uom_qty) from sale_order_line where id in %s" , (tuple(sale_order_line_ids),))
                            res_total_sale = cr.fetchall()
                            if res_total_sale and res_total_sale[0] and res_total_sale[0][0]:
                                categ_amt_sale = res_total_sale[0][0]
                            for sale in sale_order_obj.browse(cr, uid, sale_order_user_ids):
                                for order in sale.order_line:
                                    if order and order.product_id and order.product_id.categ_id and order.product_id.categ_id.cost_center_id:
                                        if order.product_id.categ_id.cost_center_id.name not in cost_center_list:
                                            cost_center_list.append(order.product_id.categ_id.cost_center_id.name)
                        percentage = 0.00
                        if categ_amt_sale and total_amt_sale:
                            percentage = categ_amt_sale / total_amt_sale * 100
                        cpfsdl_amt_categ_amt = fwl_amt_categ_amt = cpfer_amt_categ_amt = cpfee_amt_categ_amt = cpf_amt_categ_amt = bonus_amt_categ_amt = gross_amt_categ_amt = incentive_amt_categ_amt = net_amt_categ_amt = supmgr_amt_categ_amt = commission_amt_categ_amt = allowance_amt_categ_amt = overtime_amt_categ_amt = basic_salary_categ_amt = 0.00
                        payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', employee.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('state', 'in', ['draft', 'verify', 'done'])])
                        cpfsdl_amt_categ = fwl_amt_categ = cpfer_amt_categ = cpfee_amt_categ = basic_salary_categ = cpf_amt_categ = bonus_amt_categ = gross_amt_categ = incentive_amt_categ = net_amt_categ = supmgr_amt_categ = commission_amt_categ = allowance_amt_categ = overtime_amt_categ = 0.00
                        if payslip_ids:
                            for line in payslip_obj.browse(cr, uid, payslip_ids[0]).line_ids:
                                if line.code == 'BASIC':
                                    basic_salary_categ += line.amount
                                if line.code == 'SC102':
                                    overtime_amt_categ += line.amount
                                if line.code in ['SC106', 'SC108', 'SC123']:
                                    allowance_amt_categ += line.amount
                                if line.code == 'SC104':
                                    commission_amt_categ += line.amount
                                if line.code == 'SC105':
                                    incentive_amt_categ += line.amount
                                if line.code == 'SC121':
                                    bonus_amt_categ += line.amount
                                if line.code == 'GROSS':
                                    gross_amt_categ += line.amount
                                if line.code == 'CPFEE' or line.category_id.code == 'CAT_CPF_EMPLOYEE':
                                    cpf_amt_categ += line.amount
                                if line.code == 'NET':
                                    net_amt_categ += line.amount
                                if line.code == 'SC108':
                                    supmgr_amt_categ += line.amount
                                
                                if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                                    cpfee_amt_categ += line.amount
                                if line.category_id.code == 'CAT_CPF_EMPLOYER':
                                    cpfer_amt_categ += line.amount
                                if line.category_id.code == 'CATCPFAGENCYSERVICESER':
                                    fwl_amt_categ += line.amount
                                if line.code == 'CPFSDL':
                                    cpfsdl_amt_categ += line.amount
                        
                        cpfsdl_amt_categ_amt = cpfsdl_amt_categ * percentage / 100
                        emp_cpfsdl_amt_categ += cpfsdl_amt_categ_amt
                        
                        cpfee_amt_categ_amt = cpfee_amt_categ * percentage / 100
                        emp_cpfee_amt_categ += cpfee_amt_categ_amt
                        
                        cpfer_amt_categ_amt = cpfer_amt_categ * percentage / 100
                        emp_cpfer_amt_categ += cpfer_amt_categ_amt
                        
                        fwl_amt_categ_amt = fwl_amt_categ * percentage / 100
                        emp_fwl_amt_categ += fwl_amt_categ_amt
                        
                        
                        basic_salary_categ_amt = basic_salary_categ * percentage / 100
                        emp_basic_salary_amt += basic_salary_categ_amt
                        
                        cpf_amt_categ_amt = cpf_amt_categ * percentage / 100
                        emp_cpf_amt += cpf_amt_categ_amt
                        
                        bonus_amt_categ_amt = bonus_amt_categ * percentage / 100
                        emp_bonus_amt += bonus_amt_categ_amt
                        
                        gross_amt_categ_amt = gross_amt_categ * percentage / 100
                        emp_gross_amt += gross_amt_categ_amt
                        
                        incentive_amt_categ_amt = incentive_amt_categ * percentage / 100
                        emp_incentive_amt += incentive_amt_categ_amt
                        
                        net_amt_categ_amt = net_amt_categ * percentage / 100
                        emp_net_amt += net_amt_categ_amt
                        
                        supmgr_amt_categ_amt = supmgr_amt_categ * percentage / 100
                        emp_supmgr_amt += supmgr_amt_categ_amt
                        
                        commission_amt_categ_amt = commission_amt_categ * percentage / 100
                        emp_commission_amt += commission_amt_categ_amt
                        
                        allowance_amt_categ_amt = allowance_amt_categ * percentage / 100
                        emp_allowance_amt += allowance_amt_categ_amt
                        
                        overtime_amt_categ_amt = overtime_amt_categ * percentage / 100
                        emp_overtime_amt += overtime_amt_categ_amt
                        
                tot_emp_basic_salary_amt += emp_basic_salary_amt
                tot_emp_overtime_amt += emp_overtime_amt
                tot_emp_allowance_amt += emp_allowance_amt
                tot_emp_commission_amt += emp_commission_amt
                tot_emp_net_amt += emp_net_amt
                tot_emp_incentive_amt += emp_incentive_amt
                tot_emp_gross_amt += emp_gross_amt
                tot_emp_bonus_amt += emp_bonus_amt
                tot_emp_cpf_amt += emp_cpf_amt
                tot_emp_supmgr_amt += emp_supmgr_amt
                
                tot_emp_fwl_amt_categ += emp_fwl_amt_categ
                tot_emp_cpfer_amt_categ += emp_cpfer_amt_categ
                tot_emp_cpfee_amt_categ += emp_cpfee_amt_categ
                tot_emp_cpfsdl_amt_categ += emp_cpfsdl_amt_categ
                
                if len(cost_center_list) > 0:
                    for cc in cost_center_list:
                        prom_pay_row += 1
                        prom_pay_worksheet.write(prom_pay_row, 0, tools.ustr(categ_no), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 1, tools.ustr(categ.name or ''), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 2, 'GEN', promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 3, tools.ustr(cc or ''), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 4, round(emp_basic_salary_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 5, round(emp_overtime_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 6, round(emp_allowance_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 7, round(emp_supmgr_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 8, round(emp_commission_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 9, round(emp_incentive_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 10, round(emp_bonus_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 11, round(emp_gross_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 12, round(emp_cpf_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_pay_worksheet.write(prom_pay_row, 13, round(emp_net_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        
                        prom_cpf_row += 1
                        prom_cpf_worksheet.write(prom_cpf_row, 0, tools.ustr(categ_no), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 1, tools.ustr(categ.name or ''), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 2, 'GEN', promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 3, tools.ustr(cc or ''), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 4, round(emp_cpfee_amt_categ / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 5, round(emp_cpfer_amt_categ / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 6, round(emp_cpfsdl_amt_categ / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 7, round(emp_fwl_amt_categ / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        prom_cpf_worksheet.write(prom_cpf_row, 8, round(emp_net_amt / len(cost_center_list) or 0.00, 2), promo_header_bold_off)
                        categ_no += 1
                else:
                    prom_pay_row += 1
                    prom_pay_worksheet.write(prom_pay_row, 0, tools.ustr(categ_no), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 1, tools.ustr(categ.name), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 2, 'GEN', promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 3, '', promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 4, round(emp_basic_salary_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 5, round(emp_overtime_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 6, round(emp_allowance_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 7, round(emp_supmgr_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 8, round(emp_commission_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 9, round(emp_incentive_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 10, round(emp_bonus_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 11, round(emp_gross_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 12, round(emp_cpf_amt or 0.00, 2), promo_header_bold_off)
                    prom_pay_worksheet.write(prom_pay_row, 13, round(emp_net_amt or 0.00, 2), promo_header_bold_off)
                    
                    prom_cpf_row += 1
                    prom_cpf_worksheet.write(prom_cpf_row, 0, tools.ustr(categ_no), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 1, tools.ustr(categ.name or ''), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 2, 'GEN', promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 3, '', promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 4, round(emp_cpfee_amt_categ or 0.00, 2), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 5, round(emp_cpfer_amt_categ or 0.00, 2), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 6, round(emp_cpfsdl_amt_categ or 0.00, 2), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 7, round(emp_fwl_amt_categ or 0.00, 2), promo_header_bold_off)
                    prom_cpf_worksheet.write(prom_cpf_row, 8, round(emp_net_amt or 0.00, 2), promo_header_bold_off)
                    categ_no += 1
            
            prom_pay_row += 2
            prom_pay_worksheet.write(prom_pay_row, 1, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 2, '', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 3, 'TOTAL', promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 4, round(tot_emp_basic_salary_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 5, round(tot_emp_overtime_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 6, round(tot_emp_allowance_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 7, round(tot_emp_supmgr_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 8, round(tot_emp_commission_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 9, round(tot_emp_incentive_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 10, round(tot_emp_bonus_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 11, round(tot_emp_gross_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 12, round(tot_emp_cpf_amt or 0.00, 2), promo_header_bold)
            prom_pay_worksheet.write(prom_pay_row, 13, round(tot_emp_net_amt or 0.00, 2), promo_header_bold)
            
            prom_cpf_row += 2
            prom_cpf_worksheet.write(prom_cpf_row, 1, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 2, '', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 3, 'TOTAL', promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 4, round(tot_emp_cpfee_amt_categ or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 5, round(tot_emp_cpfer_amt_categ or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 6, round(tot_emp_cpfsdl_amt_categ or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 7, round(tot_emp_fwl_amt_categ or 0.00, 2), promo_header_bold)
            prom_cpf_worksheet.write(prom_cpf_row, 8, round(tot_emp_net_amt or 0.00, 2), promo_header_bold)
            
            grand_tot_emp_basic_salary_amt += tot_emp_basic_salary_amt
            grand_tot_emp_overtime_amt += tot_emp_overtime_amt
            grand_tot_emp_allowance_amt += tot_emp_allowance_amt
            grand_tot_emp_commission_amt += tot_emp_commission_amt
            grand_tot_emp_net_amt += tot_emp_net_amt
            grand_tot_emp_incentive_amt += tot_emp_incentive_amt
            grand_tot_emp_gross_amt += tot_emp_gross_amt
            grand_tot_emp_bonus_amt += tot_emp_bonus_amt
            grand_tot_emp_cpf_amt += tot_emp_cpf_amt
            grand_tot_emp_supmgr_amt += tot_emp_supmgr_amt
            
            grand_tot_emp_fwl_amt_categ += tot_emp_fwl_amt_categ
            grand_tot_emp_cpfer_amt_categ += tot_emp_cpfer_amt_categ
            grand_tot_emp_cpfee_amt_categ += tot_emp_cpfee_amt_categ
            grand_tot_emp_cpfsdl_amt_categ += tot_emp_cpfsdl_amt_categ
            
            prom_pay_row += 5
            prom_cpf_row += 5
            
        
        prom_pay_row += 1
        prom_pay_worksheet.write(prom_pay_row, 1, '', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 2, 'GRAND TOTAL', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 3, '', promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 4, round(grand_tot_emp_basic_salary_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 5, round(grand_tot_emp_overtime_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 6, round(grand_tot_emp_allowance_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 7, round(grand_tot_emp_supmgr_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 8, round(grand_tot_emp_commission_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 9, round(grand_tot_emp_incentive_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 10, round(grand_tot_emp_bonus_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 11, round(grand_tot_emp_gross_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 12, round(grand_tot_emp_cpf_amt or 0.00, 2), promo_header_bold)
        prom_pay_worksheet.write(prom_pay_row, 13, round(grand_tot_emp_net_amt or 0.00, 2), promo_header_bold)
        
        prom_cpf_row += 1
        prom_cpf_worksheet.write(prom_cpf_row, 1, '', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 2, 'GRAND TOTAL', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 3, '', promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 4, round(grand_tot_emp_cpfee_amt_categ or 0.00, 2), promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 5, round(grand_tot_emp_cpfer_amt_categ or 0.00, 2), promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 6, round(grand_tot_emp_cpfsdl_amt_categ or 0.00, 2), promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 7, round(grand_tot_emp_fwl_amt_categ or 0.00, 2), promo_header_bold)
        prom_cpf_worksheet.write(prom_cpf_row, 8, round(grand_tot_emp_net_amt or 0.00, 2), promo_header_bold)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)


    def _get_file_name(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        period_id = context.get('period_from')
        if not period_id:
            return 'PR/WH  Payroll Summary.xls'
        period_data = period_obj.browse(cr, uid, period_id[0], context=context)
        end_date = datetime.datetime.strptime(period_data.date_stop, DEFAULT_SERVER_DATE_FORMAT)
        monthyear = end_date.strftime('%b%Y')
        file_name = 'PR/WH  Payroll Summary ' + monthyear + '.xls'
        return file_name

    _columns = {
        'period_from': fields.many2one('account.period', 'Period From'),
        'file': fields.binary("Click On Save As Button To Download File", readonly=True),
        'is_generate': fields.boolean('Is Generate?', invisible=True),
        'name': fields.char("Name" , size=256, readonly=True, invisible=True)
    }

    def export_pr_wh_payroll_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        context.update({'period_from': data['period_from']})
        self.write(cr, uid, ids, {'is_generate': True,
                                  'name': self._get_file_name(cr, uid, context),
                                  'file': self._get_pr_wh_payroll_report_data(cr, uid, context)})
        return False

    _defaults = {
        'name': 'PR/WH  Payroll Summary.xls',
    }

pr_wh_payroll_summary()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
