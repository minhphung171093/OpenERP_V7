from osv import osv, fields
from tools.translate import _
import base64
import cStringIO
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
import tools
import xlwt

class payslip_sample_wiz(osv.osv):

    _name = 'payslip.sample.wiz'

    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'ihrms_hr_employee_payslip_sample_rel','emp_id','employee_id','Employee Name', required=False),
        'period_id': fields.many2one('account.period','Period', required=True),
    }

    def print_payslip_sample_excel_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids, [])[0]
        context.update({'employe_id': data['employee_ids'], 'period_id': data['period_id']})
        return {
              'name': _('Binary'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'payslip.sample.excel.file',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
              }

payslip_sample_wiz()

class payslip_sample_excel_file(osv.osv_memory):
    
    _name = 'payslip.sample.excel.file'
    
    _columns = {
            'name': fields.char('Filename', 16, invisible=True),
            'file': fields.binary('File',readonly=True), 
    }
    
    def _generate_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        period_obj = self.pool.get('account.period')
        payslip_obj = self.pool.get('hr.payslip')
        employee_id = context.get('employe_id')
        employe_obj = self.pool.get('hr.employee')
        period_id = context.get('period_id')
        period = period_obj.browse(cr, uid, period_id[0])
        year=period.fiscalyear_id.name
        first_date = '%s-01-01'%(year)
        year_first_date = datetime.datetime.strptime(first_date, DEFAULT_SERVER_DATE_FORMAT)
        start_date = datetime.datetime.strptime(period.date_start, DEFAULT_SERVER_DATE_FORMAT)
        start_date_formate = start_date.strftime('%B-%Y')
        payslip_ids = payslip_obj.search(cr, uid, [('employee_id','in',employee_id),('date_from', '>=', period.date_start), ('date_from','<=',period.date_stop), ('state', 'in', ['done', 'verify', 'draft'])])
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
#        pattern = xlwt.Pattern() # Create the Pattern
#        pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
#        pattern.pattern_fore_colour = 5 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
#        
        style = xlwt.easyxf('align: wrap no;font: height 200, color 23;')
#        style.pattern = pattern # Add Pattern to Style
        style.num_format_str = '0.00'
        style_right = xlwt.easyxf('align: wrap no;font: height 200, color 23;')
        style_right.num_format_str = '0.00'
        alignment = xlwt.Alignment() # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style_right.alignment = alignment
        row_number = 0
        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
            current_payslip_row = 0
            employee_name_code = 'Name : '
            employee_name = str(payslip.employee_id.name)
            employee_identification_id_code = 'Emp : '
            employee_identification_id = str(payslip.employee_id.identification_id)
            if str(employee_identification_id) == 'False':
                employee_identification_id = 'Nil'

            employee_contract_id_code = 'Contract : ' 
            employee_contract_id = str(payslip.contract_id.name)
            company_name = 'Prestige Products Distribution Pte Ltd '
            employee_data = employe_obj.browse(cr, uid, payslip.employee_id.id)
            category_name =  str(employee_data.category_ids and employee_data.category_ids[0].name or '')
            date_sheet = str(start_date_formate)
            worksheet.write(row_number, 0, employee_name_code + tools.ustr(employee_name) + "        " + tools.ustr(employee_identification_id_code) 
                            + tools.ustr(employee_identification_id) , style)
            worksheet.write(row_number, 7, tools.ustr(employee_contract_id_code) + tools.ustr(employee_contract_id), style)
            row_number = row_number+1
            current_payslip_row += 1
            worksheet.write(row_number, 0, company_name, style)
            worksheet.write(row_number, 6, "Category : " + category_name, style)
            worksheet.write(row_number, 8, date_sheet, style)
            
            row_number = row_number+2
            current_payslip_row += 2
            basic_amount = ftot_amt = upl_amount_rate = total_wage = basic_category_amount = 0.0
            total_wage_slip_code = total_wage_code = ''
            for line in payslip.line_ids:
                if line.code == 'BASIC':
                    total_wage_code = line.name
                    total_wage = abs(line.total)
                    basic_amount = round(line.total or 0.0,2)
                if line.category_id.code == 'BASIC':
                    basic_category_amount += line.total
#                if line.code == 'CPFEE':
#                    employee_cpf_code = line.name
#                    employee_cpf = abs(line.total)
#                if line.code == 'SC102':
#                    employee_otc_code = line.name
#                    employee_otc = abs(line.total)
#                
#                if line.code == 'SC206':
#                    employee_upl_code = line.name
#                    employee_upl = abs(line.total)
#                
#            for line in payslip.line_ids:
#                if line.code == 'BASIC':
                    
#                if line.code == 'SC102':
#                    total_overtime_amount = round(line.total or 0.0, 2)
            upl_days = TTLDAYINMTH = TTLSUNINMONTH = 0
            for line in payslip.worked_days_line_ids:
                if line.code == 'UPL':
                    upl_days = round(line.number_of_days or 0.0 ,2)
                if line.code == 'TTLDAYINMTH':
                    TTLDAYINMTH = round(line.number_of_days or 0.0 ,2)
                if line.code == 'TTLSUNINMONTH':
                    TTLSUNINMONTH = round(line.number_of_days or 0.0 ,2)

            if upl_days > 0:
                upl_amount_rate =  round(basic_amount / (TTLDAYINMTH - TTLSUNINMONTH) * 1, 2)
            overtime_rate = ((basic_category_amount *12 / 2288) * 1.5 * 1)
            overtime_rate = overtime_rate.__trunc__()  + (((overtime_rate % 1) * 100 ).__trunc__()) * 0.01

            for input in payslip.input_line_ids:
                if input.code == 'SC102I':
                    ftot_amt = round(abs(input.amount) or 0.0, 2)

            worksheet.write(row_number, 0, "Basic  :  ", style)
            worksheet.write(row_number, 4, payslip.contract_id.wage, style)
#                worksheet.write(row_number, 1, tools.ustr(total_wage_slip_code) + tools.ustr(total_wage_slip), style)
#            if employee_cpf_code:
#                employee_cpf_slip_code = employee_cpf_code  
#                employee_cpf_slip = employee_cpf
#                worksheet.write(row_number, 3, employee_cpf_slip_code, style)
#                worksheet.write(row_number, 5, employee_cpf_slip, style)
#                worksheet.write(row_number, 5, tools.ustr(employee_cpf_slip_code) + tools.ustr(employee_cpf_slip), style)
#            if employee_otc_code:
#                employee_otc_total = employee_otc_code + ' ' + str(overtime_rate) + ' @ ' + str(abs(ftot_amt))
#            if employee_upl_code:
#                employee_upl_deduction = employee_upl_code + ' : ' + str(upl_days) + 'Days @ ' + str(abs(upl_amount_rate)) 
#            
#            row_number = row_number+1
#            worksheet.write(row_number, 0, employee_otc_total, style)
#            worksheet.write(row_number, 2, total_overtime_amount, style)
#            worksheet.write(row_number, 3, employee_upl_deduction, style)
#            worksheet.write(row_number, 6, employee_upl, style)
            row_number = row_number+1
            current_payslip_row += 2
            row_number = row_number+1
            allowance = 'Addition : '
            worksheet.write(row_number, 0, allowance, style)
            allowance_list = []
            allowance_dict = {}
            
#            basic_seq_no = gross_seq_no = net_seq_no = 0
#            gross_seq_no = 200
#            for line in payslip.line_ids:
#                if line.code == 'BASIC':
#                    basic_seq_no = line.sequence
##                if line.code == 'GROSS':
##                    gross_seq_no = line.sequence
#                if line.code == 'NET':
#                    net_seq_no = line.sequence
            
            for line in payslip.line_ids:
                if line.code == 'BASIC':
                    continue
                if line.category_id and (line.category_id.code == 'ADD' or line.category_id.code == 'BASIC'):
                    sl_name = line.name
                    sl_amount = abs(line.total or 0.0)
                    if line.name.startswith('services') or line.name.startswith('Services'):
                        sl_name = "Services"
                        sl_amount = line.total or 0.0
                    if line.code == 'SC102':
                        split_total_rule = str(overtime_rate)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
                        split_total_rule1 = str(ftot_amt)
                        split_total_rule1 = split_total_rule1.ljust(len(split_total_rule1.split('.')[0])+3, '0')

                        sl_name = line.name + ' ' + str(split_total_rule) + ' @ ' + str(split_total_rule1)
                    allowance_dict = {
                           'name': sl_name,
                           'total': round(sl_amount, 2),
                    }
                    allowance_list.append(allowance_dict)
            allowance_row_number = 0
            allowance_count = 0
            allowance_row_number = row_number+1
            cur_all_row = (payslip_ids.index(payslip.id) * 17) +13
            if allowance_list:
                for salary_rule in allowance_list:
                    allowance_count+=1
                    
                    if cur_all_row <= allowance_row_number:
                        break
                    salary_rule_name = salary_rule['name'] 
                    salary_total = str(salary_rule['total'])
                    worksheet.write(allowance_row_number, 0, salary_rule_name, style)
                    worksheet.write(allowance_row_number, 4, float(salary_total), style)
#                    worksheet.write(allowance_row_number, 1, salary_rule_name + "     " + tools.ustr(abs(float(salary_total))), style)
                    allowance_row_number = allowance_row_number+1
                    
            
            deduction = 'Deduction : '
            worksheet.write(row_number, 6, deduction, style)
            deduction_list = []
            deduction_dict = {}
            for line in payslip.line_ids:
                if line.category_id and (line.category_id.code == 'DED' or line.category_id.code == 'CAT_CPF_EMPLOYEE'
                                         or line.category_id.code == 'CATCPFAGENCYSERVICESEE' or line.category_id.code == 'DED_INCL_CPF'):
                    if line.code == 'CPFTOTAL' or line.code == 'CPFER':
                        continue
                    sl_name = line.name
                    if line.name.startswith('services') or line.name.startswith('Services'):
                        sl_name = "Services"
                    if line.code == 'SC206':
                        split_total_rule = str(upl_days)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0])+3, '0')
                        split_total_rule1 = str(upl_amount_rate)
                        split_total_rule1 = split_total_rule1.ljust(len(split_total_rule1.split('.')[0])+3, '0')

                        sl_name = line.name + ' : ' + str(split_total_rule) + 'Days @ ' + str(split_total_rule1)
                    deduction_dict = {
                           'name': sl_name,
                           'total': round(abs(line.total) or 0.0, 2),
                    }
                    deduction_list.append(deduction_dict)
            deduction_row_number = 0
            deduction_count = 0
            deduction_row_number = row_number+1
            if deduction_list:
                for salary_rule in deduction_list:
                    deduction_count+=1
                    
                    if cur_all_row <= allowance_row_number:
                        break
                    salary_rule_name = salary_rule['name'] + ' : ' 
                    salary_total = str(salary_rule['total'])
                    worksheet.write(deduction_row_number, 6, salary_rule_name, style)
                    worksheet.write(deduction_row_number, 8, abs(float(salary_total)), style)
#                    worksheet.write(deduction_row_number, 5, salary_rule_name + "        " + tools.ustr(abs(float(salary_total))), style)
                    deduction_row_number = deduction_row_number+1

#            if allowance_count > deduction_count:
#                temp_row_number = cur_all_row + 1
#            else:
#                temp_row_number = cur_did_row + 1
#            if temp_row_number < 14:
#                inc = (14 - temp_row_number)
            row_number = (payslip_ids.index(payslip.id) * 17) + 13 
#            current_ytd_name = 'CURRENT  /  YTD'
            worksheet.write(row_number, 7, 'CURRENT', style_right)
            worksheet.write(row_number, 8, 'YTD', style_right)
            bank_detail = ''
            month_wage = ytd_wage = month_gross = ytd_gross = totalytd_cpf = month_totalcpf = 0.0
            gross_code = net_code = totalcpf_code = ''
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_code = line.name
                    month_wage = round(abs(line.total) or 0.0, 2)
                
                if line.code == 'GROSS':
                    gross_code = line.name
                    month_gross = round(abs(line.total) or 0.0 ,2)
                
                if line.category_id.code == 'CAT_CPF_TOTAL':
                    totalcpf_code = line.name
                    month_totalcpf = round(abs(line.total) or 0.0, 2)
            payslip_search = payslip_obj.search(cr, uid, [('employee_id','=',payslip.employee_id.id), ('state', 'in', ['draft', 'done', 'verify']),('date_from','>=',year_first_date),('date_to','<=',payslip.date_to)])
            for hr_payslip in payslip_obj.browse(cr, uid, payslip_search):
                for line in hr_payslip.line_ids:
                    if line.code == 'NET':
                        ytd_wage += round(abs(line.total) or 0.0, 2)
                    if line.code == 'GROSS':
                        ytd_gross += round(abs(line.total) or 0.0, 2)
                    if line.code in ['CPFTOTAL']:
                        totalytd_cpf += round(abs(line.total) or 0.0, 2)
            
            if net_code:
                net_code = net_code + '     : '
                row_number = row_number+1
                worksheet.write(row_number, 6, net_code, style)
                worksheet.write(row_number, 7, month_wage, style)
                worksheet.write(row_number, 8, abs(float(ytd_wage)), style)
#                worksheet.write(row_number, 5, net_code + "     " + tools.ustr(net_wage) + "     " +  tools.ustr( abs(float(ytd_wage))), style)
            if gross_code:
                gross_code = gross_code + ' : '
                row_number = row_number+1
                worksheet.write(row_number, 6, gross_code, style)
                worksheet.write(row_number, 7, month_gross, style)
                worksheet.write(row_number, 8, abs(float(ytd_gross)), style)
#                worksheet.write(row_number, 5, gross_code + "     " + tools.ustr(net_gross) + "     " + tools.ustr(abs(float(ytd_gross))), style)
            
            bank_code = branch_code = bank_acc_no = 0
            row_number = row_number+1
            if payslip.employee_id:
                employe_data = employe_obj.browse(cr, uid, payslip.employee_id.id)
                for bank in employe_data.bank_detail_ids:
                    bank_code = bank.bank_code
                    branch_code = bank.branch_code
                    bank_acc_no = bank.bank_ac_no
            if bank_code or branch_code or bank_acc_no:
                bank_detail = 'Bank : ' 
                bank_code = str(bank_code)
                branch_code = str(branch_code)
                bank_acc_no = str(bank_acc_no)
                worksheet.write(row_number, 0, bank_detail + "    " + tools.ustr(bank_code)  + "    " + tools.ustr(branch_code) + "    "  + tools.ustr(bank_acc_no), style)
            
            if totalcpf_code:
                totalcpf_code = totalcpf_code + ' :'
                worksheet.write(row_number, 6, totalcpf_code, style)
                worksheet.write(row_number, 7, month_totalcpf, style)
                worksheet.write(row_number, 8, abs(float(totalytd_cpf)), style)
#                worksheet.write(row_number, 5, totalcpf_code  + "    " + tools.ustr(total_cpf)  + "    " + tools.ustr(abs(float(totalytd_cpf))), style)
            
            row_number = row_number + 1
        
        fp = cStringIO.StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = base64.encodestring(fp.getvalue())
        fp.close()
        return data
    
    _defaults = {
                'file': _generate_file,
                'name': 'Payslip.xls',
    }
    
payslip_sample_excel_file()