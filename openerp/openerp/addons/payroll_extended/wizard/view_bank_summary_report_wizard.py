from osv import osv, fields
import tools
from tools.translate import _
import base64
import xlwt
from cStringIO import StringIO
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
import locale

class excel_export_summay(osv.osv_memory):
    _name = "excel.export.summay"
    
    def _get_excel_export_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        bank_obj = self.pool.get('hr.bank.details')
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        res_user = self.pool.get("res.users").browse(cr, uid,uid,context=context)
        start_date = datetime.datetime.strptime(context.get("date_from"), DEFAULT_SERVER_DATE_FORMAT)
        start_date_formate = start_date.strftime('%d/%m/%Y')
        end_date = datetime.datetime.strptime(context.get("date_to"), DEFAULT_SERVER_DATE_FORMAT)
        end_date_formate = end_date.strftime('%d/%m/%Y')
        start_date_to_end_date = tools.ustr(start_date_formate) + ' To ' + tools.ustr(end_date_formate)
        
        style = xlwt.easyxf('align: wrap yes')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.write(0, 0, "Company Name" , header)
        worksheet.write(0, 1, res_user.company_id.name,header)
        worksheet.write(0, 7, "By Bank",header)
        worksheet.write(1, 0, "Period",header)
        worksheet.write(1, 1, start_date_to_end_date,header)
        worksheet.col(9).width = 5000
        worksheet.col(11).width = 5000
        
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle() # Create Style
        border_style.borders = borders
        row = 2
        payslip_obj = self.pool.get('hr.payslip')
        employee_obj = self.pool.get('hr.employee')
        hr_depart_obj = self.pool.get('hr.department')
        employee_ids = employee_obj.search(cr, uid, [('bank_detail_ids','!=',False), ('id', 'in', context.get("employee_ids")), ('department_id', '=', False)])
        new_employee_ids = []
        style = xlwt.easyxf('align: wrap yes',style)
        if employee_ids:
            payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', context.get("date_from")), ('date_from','<=',context.get("date_to")),
                                                       ('employee_id', 'in' , employee_ids), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
            if payslip_ids:
                bank_ids = bank_obj.search(cr, uid, [('bank_emp_id', 'in', employee_ids)], order="bank_name, bank_code, branch_code")
                for bank in bank_obj.browse(cr, uid, bank_ids):
                    if bank.bank_emp_id.id not in new_employee_ids:
                        new_employee_ids.append(bank.bank_emp_id.id)
                blank_emp_ids = list(set(employee_ids).difference(set(new_employee_ids)))
                new_employee_ids += blank_emp_ids
    
                row = 4
                worksheet.write(4, 0, "",border_style)
                worksheet.write(4, 1, "Employee Name" ,border_style)
                worksheet.write(4, 2, "",border_style)
                worksheet.write(4, 3, "Employee Login"  , border_style)
                worksheet.write(4, 4, "",border_style)
                worksheet.write(4, 5, "Amount" ,border_style)
                worksheet.write(4, 6, "",border_style)
                worksheet.write(4, 7, "Name Of Bank",border_style)
                worksheet.write(4, 8, "",border_style)
                worksheet.write(4, 9, "Bank Code",border_style)
                worksheet.write(4, 10, "",border_style)
                worksheet.write(4, 11, "Account Number",border_style)
                worksheet.write(4, 12, "",border_style)
                worksheet.write(4, 13, "Branch Code",border_style)
                row += 1

        hr_department_search_id =  hr_depart_obj.search(cr, uid, [])
        result = {}
        payslip_data= {}
        
        department_total_amount = 0.0
        for employee in employee_obj.browse(cr, uid, new_employee_ids):
            payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', context.get("date_from")), ('date_from','<=',context.get("date_to")),
                                                       ('employee_id', '=' , employee.id), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
            net = 0.00
            if not payslip_ids:
                continue
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                for line in payslip.line_ids:
                    if line.code == 'NET':
                        net += line.total
            print "::::::::::::", employee, employee.bank_detail_ids
            net_total = '%.2f' % net
            worksheet.write(row, 1, employee.name )
            worksheet.write(row, 2, "")
            worksheet.write(row, 3, employee and employee.user_id and employee.user_id.login or '' )
            worksheet.write(row, 4, "")
            worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(net_total), grouping=True)) )
            worksheet.write(row, 6, "")
            worksheet.write(row, 7, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_name or ''  )
            worksheet.write(row, 8, "")
            worksheet.write(row, 9, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_code or '')
            worksheet.write(row, 10, "")
            worksheet.write(row, 11, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_ac_no or '' )
            worksheet.write(row, 12, "")
            worksheet.write(row, 13, employee.bank_detail_ids and employee.bank_detail_ids[0].branch_code or '')
#            worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(net_total))
            row+=1
            department_total_amount += net
            if 'Undefine' in result:
                result.get('Undefine').append(payslip_data)
            else:
                result.update({'Undefine': [payslip_data]})
        if department_total_amount:
            worksheet.write(row, 0, 'Total Undefine',border_style)
            worksheet.write(row, 1, '',border_style)
            worksheet.write(row, 2, '',border_style)
            worksheet.write(row, 3, '',border_style)
            worksheet.write(row, 4, '',border_style)
            worksheet.write(row, 5, '',border_style)
            worksheet.write(row, 6, '',border_style)
            worksheet.write(row, 7, '',border_style)
            worksheet.write(row, 8, '',border_style)
            worksheet.write(row, 9, '',border_style)
            worksheet.write(row, 10, '',border_style)
            worksheet.write(row, 11, '',border_style)
            worksheet.write(row, 12, '',border_style)
            new_department_total_amount = '%.2f' % department_total_amount
            worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)) ,border_style)
            row+=1
        new_department_total_amount1 = '%.2f' % department_total_amount
        department_total = {'total': new_department_total_amount1, 'department_name': 'Total Undefine'}
        department_info = {'Undefine': [department_total]}

        for hr_department in hr_depart_obj.browse(cr, uid, hr_department_search_id):
            employee_ids = employee_obj.search(cr, uid, [('bank_detail_ids','!=',False), ('id', 'in', context.get("employee_ids")), ('department_id', '=', hr_department.id)])
            new_employee_ids = []
            bank_ids = bank_obj.search(cr, uid, [('bank_emp_id', 'in', employee_ids)], order="bank_name, bank_code, branch_code")
            for bank in bank_obj.browse(cr, uid, bank_ids):
                if bank.bank_emp_id.id not in new_employee_ids:
                    new_employee_ids.append(bank.bank_emp_id.id)
            blank_emp_ids = list(set(employee_ids).difference(set(new_employee_ids)))
            new_employee_ids += blank_emp_ids
            department_total_amount = 0.0
            flag = False
            print_header = True
            for employee in employee_obj.browse(cr, uid, new_employee_ids, context):
                payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', context.get("date_from")), ('date_from','<=',context.get("date_to")),
                                               ('employee_id', '=' , employee.id), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
                net = 0.0
                if not payslip_ids:
                    continue
                for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                    flag = True
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
                if print_header and payslip_ids:
                    row +=2
                    print_header = False
                    worksheet.write(row, 0, "",border_style)
                    worksheet.write(row, 1, "Employee Name" ,border_style)
                    worksheet.write(row, 2, "",border_style)
                    worksheet.write(row, 3, "Employee Login"  , border_style)
                    worksheet.write(row, 4, "",border_style)
                    worksheet.write(row, 5, "Amount" ,border_style)
                    worksheet.write(row, 6, "",border_style)
                    worksheet.write(row, 7, "Name Of Bank",border_style)
                    worksheet.write(row, 8, "",border_style)
                    worksheet.write(row, 9, "Bank Code",border_style)
                    worksheet.write(row, 10, "",border_style)
                    worksheet.write(row, 11, "Account Number",border_style)
                    worksheet.write(row, 12, "",border_style)
                    worksheet.write(row, 13, "Branch Code",border_style)
                    row +=1
                new_net = '%.2f' % net
                print "::::::::::::", employee, employee.bank_detail_ids
                worksheet.write(row, 1, employee.name or '' )
                worksheet.write(row, 2, "")
                worksheet.write(row, 3, employee and employee.user_id and employee.user_id.login or '')
                worksheet.write(row, 4, "")
                worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(new_net), grouping=True)) )
                worksheet.write(row, 6, "")
                worksheet.write(row, 7, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_name or '')
                worksheet.write(row, 8, "")
                worksheet.write(row, 9, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_code or '')
                worksheet.write(row, 10, "")
                worksheet.write(row, 11, employee.bank_detail_ids and employee.bank_detail_ids[0].bank_ac_no or '')
                worksheet.write(row, 12, "")
                worksheet.write(row, 13, employee.bank_detail_ids and employee.bank_detail_ids[0].branch_code or '')
                row+=1
                department_total_amount += net
                if hr_department.id in result:
                    result.get(hr_department.id).append(payslip_data)
                else:
                    result.update({hr_department.id: [payslip_data]})
            if flag:
                worksheet.write(row, 0, tools.ustr('Total ' + hr_department.name),border_style)
                worksheet.write(row, 1, '',border_style)
                worksheet.write(row, 2, '',border_style)
                worksheet.write(row, 3, '',border_style)
                worksheet.write(row, 4, '',border_style)
                worksheet.write(row, 5, '',border_style)
                worksheet.write(row, 6, '',border_style)
                worksheet.write(row, 7, '',border_style)
                worksheet.write(row, 8, '',border_style)
                worksheet.write(row, 9, '',border_style)
                worksheet.write(row, 10, '',border_style)
                worksheet.write(row, 11, '',border_style)
                worksheet.write(row, 12, '',border_style)
                new_department_total_amount = '%.2f' % department_total_amount
                worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)), border_style)
                row+=1
            new_department_total_amount1 = '%.2f' % department_total_amount
            department_total = {'total': new_department_total_amount1, 'department_name': "Total " + hr_department.name}
            if hr_department.id in department_info:
                department_info.get(hr_department.id).append(department_total)
            else:
                department_info.update({hr_department.id: [department_total]})
                
        row +=1
        worksheet.write(row, 0, "Overall Total",border_style)
        worksheet.write(row, 1, '',border_style)
        worksheet.write(row, 2, '',border_style)
        row +=2
        for key, val in result.items():
            worksheet.write(row, 0, department_info[key][0].get("department_name"))
            worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(department_info[key][0].get("total")), grouping=True)) )
            row +=1 
        
        row+=1
        total_ammount = 0
        total_employee_ids = employee_obj.search(cr, uid, [('bank_detail_ids','!=',False), ('id', 'in', context.get("employee_ids"))])
        
        payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', context.get("date_from")), ('date_from','<=',context.get("date_to")),
                                               ('employee_id', 'in' , total_employee_ids), ('pay_by_cheque','=',False), ('state', 'in', ['draft', 'done', 'verify'])])
        if payslip_ids:
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                for line in payslip.line_ids:
                    if line.code == 'NET':
                        total_ammount+=line.total
        new_total_ammount = '%.2f' % total_ammount
        worksheet.write(row, 0, "All")
        worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(locale.format("%.2f", float(new_total_ammount), grouping=True)))
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
        'name':"Bank_summary.xls",
        'file': _get_excel_export_data
    }

class view_bank_summary_report_wizard(osv.osv):

    _name = 'view.bank.summary.report.wizard'

    _columns = {
                'employee_ids': fields.many2many('hr.employee', 'ihrms_hr_employee_bank_rel','emp_id','employee_id','Employee Name', required=False),
                'period_id': fields.many2one('account.period', 'Period', required=True),
                'export_report' : fields.selection([('pdf','PDF'),('excel','Excel')] , "Export")
    }

    _defaults = {
        'export_report': "pdf"
    }

    def print_bank_summary_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        period_obj = self.pool.get('account.period')
        period_data = period_obj.browse(cr, uid, data['period_id'][0], context=context)
        start_date = period_data.date_start
        end_date = period_data.date_stop
        if data.get("export_report") == "pdf":
            res_user = self.pool.get("res.users").browse(cr, uid,uid,context=context)
            data.update({'currency': " " + tools.ustr(res_user.company_id.currency_id.symbol), 'company': res_user.company_id.name})
            
            datas = {
                'ids': [],
                'form': data,
                'model':'hr.payslip',
                'date_from':start_date,
                'date_to':end_date
            }
            return {'type': 'ir.actions.report.xml', 'report_name': 'ppd_bank_summary_receipt', 'datas': datas}
        else:
            context.update({'employee_ids': data['employee_ids'], 'date_from': start_date, 'date_to': end_date})
            return {
              'name': _('Binary'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'excel.export.summay',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
              }

view_bank_summary_report_wizard()