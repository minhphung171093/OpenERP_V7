# -*- coding: utf-8 -*-

from osv import osv, fields
from datetime import datetime
import xlwt
import tempfile
import base64
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT
from tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta

class cpf_payment_wizard(osv.osv_memory):

    _name = 'cpf.payment.wizard'

    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'cpf_employee_rel', 'wizard_id', 'employee_id', 'Employees'),
        'period_id': fields.many2one('account.period', 'Period'),
    }

    def get_xls_file(self, cr, uid, ids, context=None):
        if context is None: context = {}
        data = self.read(cr, uid, ids, [])[0]
        period_id = False
        if data.get('period_id'):
            period_id = data.get('period_id')[0]
        context.update({'employee_id': data['employee_ids'], 'period_id': period_id })
        return {
              'name': _('XlS file'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'cpf.binary.wizard',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
        }

cpf_payment_wizard()

class cpf_binary_wizard(osv.osv_memory):
    
    _name = 'cpf.binary.wizard'
    
    _columns = {
        'name': fields.char('Name', size=256),
        'xls_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }
    
    def _default_previous_date(self,cr, uid,  date, context=None):
        date_obj = datetime.strptime(date , DEFAULT_SERVER_DATE_FORMAT)
        date_obj = date_obj - relativedelta(months=1)
        return [str(date_obj.year) + "-" + str(date_obj.month) + "-01", (date_obj + relativedelta(months=+1,day=1,days=-1)).strftime('%Y-%m-%d')]

    
    def _print_report(self, cr, uid, context=None):
        if context is None: context = {}
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
        font = xlwt.Font()
        font.bold = True
        bold_style = xlwt.XFStyle()
        bold_style.font = font
        style = xlwt.easyxf('align: wrap no')
        style.num_format_str = '#,##0.00'
        
        new_style = xlwt.easyxf('font: bold on; align: wrap no')
        new_style.num_format_str = '#,##0.00'
        # static data
        sheet.write(0, 4, 'Central Provident Fund Board')
        sheet.write(1, 3, '79 Robinson Road, CPF Building Singapore 068897')
        sheet.write(2, 3, 'P.O Box 2052, Robinson Road Post Office, Singapore 904052')
        sheet.write(3, 4, 'Tel : 1800-220-2422, Fax : 229 3881')
        sheet.write(4, 5, 'PAYMENT ADVICE')
        sheet.write(6, 0, 'MANDATORY REF NO. : 201102376WPTE01')
        sheet.write(7, 0, 'VOLUNTARY  REF NO. : ')
        sheet.write(8, 0, 'Prestige Products Distribution Pte Ltd')
        sheet.write(9, 0, '6 Jalan Kilang #04-00')
        sheet.write(6, 8, 'SUBM MODE') 
        sheet.write(7, 8, 'DATE')
        sheet.write(6, 10, ':')
        sheet.write(7, 10, ':')
        sheet.write(6, 11, 'INTERNAL')
        
        sheet.write(12, 2, 'PART 1 : Payment Details For ')
        
        sheet.write(13, 8, 'AMOUNT' , bold_style)
        sheet.write(13, 10, 'NO. OF EMPLOYEE', bold_style)
        sheet.write(15, 0, '1. CPF Contribution')
        sheet.write(16, 1, 'Mandatory Contribution')
        sheet.write(17, 1, 'Voluntary Contribution')
        sheet.write(18, 0, '2. B/F CPF late Payment interest')
        sheet.write(19, 0, 'Interest charged on last payment')
        sheet.write(20, 0, '3. Late payment interest on CPF Contribution')
        sheet.write(21, 0, '4. Late payment penalty for Foreign Worker Levy')
        sheet.write(22, 0, '5. Foreign Worker Levy')
        sheet.write(23, 0, '6. Skills Development Levy')
        sheet.write(24, 0, '7. Donation to Community Chest')
        sheet.write(25, 0, '8. Mosque Building & Mendaki Fund (MBMF)')
        sheet.write(26, 0, '9. SINDA Fund')
        sheet.write(27, 0, '10. CDAC Fund')
        sheet.write(28, 0, '11. Eurasian Community Fund (EUCF)')

        # total
        sheet.write(30, 7, 'Total', bold_style)
        # static data
        sheet.write(31, 4, 'Please fill in cheque details if you are paying by cheque')
        sheet.write(32, 4, 'BANK')
        sheet.write(32, 5, ':')
        sheet.write(33, 4, 'CHEQUE NO.')
        sheet.write(33, 5, ':')
        sheet.write(34, 4, 'THE EMPLOYER HEREBY GUARANTEES')
        sheet.write(35, 4, 'THE ACCURACY')
        sheet.write(36, 4, 'OF THE CPF RETURNS FOR')
        
        sheet.write(37, 4, 'AS SHOWN ON THE SUBMITTED DISKETTE.')
        sheet.write(39, 4, 'EMPLOYER\'S AUTHORIZED SIGNATORY')
        sheet.write(42, 0, 'PART 2 : Contribution Details For')
        
        # data header
        sheet.write(44, 0, 'Employee Name', bold_style)
        sheet.write(43, 3, 'CPF', bold_style)
        sheet.write(44, 3, 'Account No.', bold_style)
        sheet.write(43, 4, 'Mandatory CPF', bold_style)
        sheet.write(44, 4, 'Contribution', bold_style)
        sheet.write(43, 5, 'Voluntary CPF', bold_style)
        sheet.write(44, 5, 'Contribution', bold_style)
        sheet.write(43, 6, 'Last', bold_style)
        sheet.write(44, 6, 'Contribution', bold_style)
#        sheet.write(41, 8, 'CPF', bold_style)
#        sheet.write(42, 8, 'Status', bold_style)
        sheet.write(43, 8, 'MBMF', bold_style)
        sheet.write(44, 8, 'Fund', bold_style)
        sheet.write(43, 9, 'SINDA', bold_style)
        sheet.write(44, 9, 'Fund', bold_style)
        sheet.write(43, 10, 'CDAC', bold_style)
        sheet.write(44, 10, 'Fund', bold_style)
        sheet.write(43, 11, 'ECF', bold_style)
        sheet.write(44, 11, 'Fund', bold_style)
        sheet.write(43, 12, 'SDL', bold_style)
        sheet.write(44, 12, 'Fund', bold_style)
        sheet.write(43, 13, 'Ordinary', bold_style)
        sheet.write(44, 13, 'Wages', bold_style)
        sheet.write(43, 14, 'Additional', bold_style)
        sheet.write(44, 14, 'Wages', bold_style)
        
        emp_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        period_obj = self.pool.get('account.period')
        period_id = context.get('period_id')
        category_obj = self.pool.get('hr.employee.category')
        hr_contract_obj = self.pool.get('hr.contract')
        category_ids = category_obj.search(cr, uid, []) 
        start_row = raw_no = 45

        period_record = period_obj.browse(cr, uid, period_id, context)
        start_date = period_record.date_start
        stop_date = period_record.date_stop
        
        month_dict = {'01':'January', '02':'February', '03': 'March', '04':'April', '05':'May', '06':'June', '07':'July', '08':'August', '09':'September', '10':'October', '11': 'November', '12': 'December'}
        period = month_dict.get(start_date.split('-')[1]) + ', ' + start_date.split('-')[0]
        sheet.write(36, 7, period)
        sheet.write(7, 11, datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%m-%Y'))
        sheet.write(42, 3, period)
        sheet.write(12, 4, period)
        t_cpfsdl_amount = t_p_cpf_sdl_amount = t_p_fwl_amount = t_p_cpf_amount = t_gross_amount = t_ecf_amount = t_cdac_amount = t_sinda_amount = t_mbmf_amount = t_cpf_amount = 0.0
        total_cpfsdl_amount = total_p_cpf_amount = total_gross_amount = total_ecf_amount = total_cdac_amount = total_sinda_amount = total_mbmf_amount = total_cpf_amount = 0.0
        emp_cpfsdl_amount = emp_sdl_amount = emp_ecf_amount = emp_fwl_amount = emp_cdac_amount = emp_sinda_amount = emp_mbmf_amount = emp_cpf_amount = 0
        # no category
        join_date = start_date
        emp_id = emp_obj.search(cr, uid, [('id', 'in', context.get('employee_id')), ('category_ids', '=', False)])
        do_total = False
        for record in emp_obj.browse(cr, uid, emp_id, context):
            payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_from', '>=', start_date), ('date_from', '<=', stop_date) ])
            previous_date = self._default_previous_date(cr, uid, start_date, context)
            previous_payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id)], order='date_from ASC', limit=1)
            if previous_payslip_ids:
                join_date = payslip_obj.browse(cr, uid, previous_payslip_ids[0], context=context).date_from
            while(join_date <= previous_date[0]):
                previous_payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_from', '>=', previous_date[0]), ('date_from', '<=', previous_date[1])])
                if previous_payslip_ids:
                    break
                else:
                    previous_date = self._default_previous_date(cr, uid, previous_date[0], context)
            if not payslip_ids:
                continue
            payslip_record = payslip_obj.browse(cr, uid, payslip_ids[0], context)
            cpfsdl_amount = p_cpf_amount = gross_amount = ecf_amount = fwl_amount = cdac_amount = sinda_amount = mbmf_amount = cpf_amount = 0.0
            
            for line in payslip_record.line_ids:
                if line.register_id.name == 'CPF':
                    cpf_amount += line.amount
                if line.register_id.name == 'CPF - MBMF':
                    mbmf_amount += line.amount
                if line.register_id.name == 'CPF - SINDA':
                    sinda_amount += line.amount
                if line.register_id.name == 'CPF - CDAC':
                    cdac_amount += line.amount
                if line.register_id.name == 'CPF - ECF':
                    ecf_amount += line.amount
                if line.register_id.name == 'CPF - FWL':
                    fwl_amount += line.amount
                    t_p_fwl_amount += line.amount
                if line.category_id.code == 'GROSS':
                    gross_amount += line.amount
                if line.code == 'CPFSDL':
                    cpfsdl_amount += line.amount
                    t_p_cpf_sdl_amount += line.amount
            if not gross_amount:
                continue
            if not cpf_amount and not mbmf_amount and not sinda_amount and not cdac_amount and not ecf_amount and not cpfsdl_amount:
                continue
            sheet.write(raw_no, 0, payslip_record.employee_id and payslip_record.employee_id.name or '')
            sheet.write(raw_no, 3, payslip_record.employee_id and payslip_record.employee_id.identification_id or '')
                # previous cpf
            if previous_payslip_ids:
                previous_payslip_record = payslip_obj.browse(cr, uid, previous_payslip_ids[0], context)
                if payslip_record.date_from != previous_payslip_record.date_from:
                    for previous_line in previous_payslip_record.line_ids:
                        if previous_line.register_id.name == 'CPF':
                            p_cpf_amount += previous_line.amount

            # Counts Employee 
            if fwl_amount:
                emp_fwl_amount += 1
            if cpf_amount != 0:
                emp_cpf_amount += 1
            if mbmf_amount != 0:
                emp_mbmf_amount += 1
            if sinda_amount != 0:
                emp_sinda_amount += 1
            if cdac_amount != 0:
                emp_cdac_amount += 1
            if ecf_amount != 0:
                emp_ecf_amount += 1
            if cpfsdl_amount != 0:
                emp_sdl_amount += 1
            
            # writes in xls file
            do_total = True
            sheet.write(raw_no, 4, round(cpf_amount or 0.00, 2), style)
            t_cpf_amount += cpf_amount
            total_cpf_amount += cpf_amount
            sheet.write(raw_no, 5, round(0.00, 2), style)
            sheet.write(raw_no, 8, round(mbmf_amount or 0.00, 2), style)
            t_mbmf_amount += mbmf_amount
            total_mbmf_amount += mbmf_amount
            sheet.write(raw_no, 9, round(sinda_amount or 0.00, 2), style)
            t_sinda_amount += sinda_amount
            total_sinda_amount += sinda_amount
            sheet.write(raw_no, 10, round(cdac_amount or 0.00, 2), style)
            t_cdac_amount += cdac_amount
            total_cdac_amount += cdac_amount
            sheet.write(raw_no, 11, round(ecf_amount or 0.00, 2), style)
            t_ecf_amount += ecf_amount
            total_ecf_amount += ecf_amount
            sheet.write(raw_no, 12, round(cpfsdl_amount or 0.00, 2), style)
            total_cpfsdl_amount += cpfsdl_amount
            t_cpfsdl_amount += cpfsdl_amount
            sheet.write(raw_no, 13, round(gross_amount or 0.00, 2), style)
            t_gross_amount += gross_amount
            total_gross_amount += gross_amount
            sheet.write(raw_no, 6, round(p_cpf_amount or 0.00, 2), style)
            t_p_cpf_amount += p_cpf_amount
            total_p_cpf_amount += p_cpf_amount
            sheet.write(raw_no, 14, 0.00, style)
            #sheet.write(raw_no, 6, 0.00, style)
            contract_id = hr_contract_obj.search(cr, uid, [('employee_id', '=', record.id), '|', ('date_end','>=', payslip_record.date_from),('date_end','=',False)])
            old_contract_id = hr_contract_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_end','<=', payslip_record.date_from)])
            for contract in hr_contract_obj.browse(cr, uid, contract_id):
                if payslip_record.employee_id.active == False:
                    sheet.write(raw_no, 7, 'Left')
                elif contract.date_start >= payslip_record.date_from and not old_contract_id:
                    sheet.write(raw_no, 7, 'New Join')
                else:
                    sheet.write(raw_no, 7, 'Existing')
            raw_no += 1
        if do_total:
            raw_no = raw_no + 1
            sheet.write(raw_no, 0, 'Total :' , bold_style)
            start_row = start_row + 1 
            
            sheet.write(raw_no, 4, total_cpf_amount, new_style)  # cpf
            sheet.write(raw_no, 5, round(0.00, 2), style)  # v_cpf
            sheet.write(raw_no, 6, round(total_p_cpf_amount or 0.00, 2), new_style)  # p_cpf
    
            sheet.write(raw_no, 8, round(total_mbmf_amount or 0.00, 2), new_style)  # MBPF
            sheet.write(raw_no, 9, round(total_sinda_amount or 0.00, 2), new_style)  # SINDA
            sheet.write(raw_no, 10, round(total_cdac_amount or 0.00, 2), new_style)  # CDAC
            sheet.write(raw_no, 11, round(total_ecf_amount or 0.00, 2), new_style)  # ECF
            sheet.write(raw_no, 12, round(total_cpfsdl_amount or 0.00, 2), new_style)  # CPFSDL
            sheet.write(raw_no, 13, round(total_gross_amount or 0.00, 2), new_style)  # O_WAGE
            sheet.write(raw_no, 14, round(0.00, 2), style)
    #        sheet.write(raw_no, 13, xlwt.Formula("sum(N" + str(start_row) + ":N" + str(raw_no - 1) + ")"), new_style)  # AD_WAGE
        
        # emp by category
        start_row = raw_no = raw_no + 2
        
        emp_id = emp_obj.search(cr, uid, [('id', 'in', context.get('employee_id')), ('category_ids', '!=', False)])
        emp_rec = emp_obj.browse(cr, uid, emp_id, context)
        for category in category_obj.browse(cr, uid, category_ids, context):
            emp_flag= False
            total_cpfsdl_amount = total_p_cpf_amount = total_gross_amount = total_ecf_amount = total_cdac_amount = total_sinda_amount = total_mbmf_amount = total_cpf_amount = 0.0
            for record in emp_rec:
                if (record.category_ids and record.category_ids[0].id != category.id) or not record.category_ids:
                    continue
                payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_from', '>=', start_date), ('date_from', '<=', stop_date) ])
                previous_date = self._default_previous_date(cr, uid, start_date, context)
                previous_payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id)], order='date_from ASC', limit=1)
                if previous_payslip_ids:
                    join_date = payslip_obj.browse(cr, uid, previous_payslip_ids[0], context=context).date_from
                while(join_date <= previous_date[0]):
                    previous_payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_from', '>=', previous_date[0]), ('date_from', '<=', previous_date[1])])
                    if previous_payslip_ids:
                        break
                    else:
                        previous_date = self._default_previous_date(cr, uid, previous_date[0], context)
                if not payslip_ids:
                    continue
                payslip_record = payslip_obj.browse(cr, uid, payslip_ids[0], context)
                cpfsdl_amount = p_cpf_amount = gross_amount = ecf_amount = fwl_amount = cdac_amount = sinda_amount = mbmf_amount = cpf_amount = 0.0
                
                for line in payslip_record.line_ids:
                    if line.register_id.name == 'CPF':
                        cpf_amount += line.amount
                    if line.register_id.name == 'CPF - MBMF':
                        mbmf_amount += line.amount
                    if line.register_id.name == 'CPF - SINDA':
                        sinda_amount += line.amount
                    if line.register_id.name == 'CPF - CDAC':
                        cdac_amount += line.amount
                    if line.register_id.name == 'CPF - ECF':
                        ecf_amount += line.amount
                    if line.register_id.name == 'CPF - FWL':
                        fwl_amount += line.amount
                        t_p_fwl_amount += line.amount
                    if line.category_id.code == 'GROSS':
                        gross_amount += line.amount
                    if line.code == 'CPFSDL':
                        cpfsdl_amount += line.amount
                        t_p_cpf_sdl_amount += line.amount

                if not gross_amount:
                    continue
                if not cpf_amount and not mbmf_amount and not sinda_amount and not cdac_amount and not ecf_amount and not cpfsdl_amount:
                    t_p_fwl_amount -= fwl_amount
                    continue
                sheet.write(raw_no, 0, payslip_record.employee_id and payslip_record.employee_id.name or '')
                sheet.write(raw_no, 3, payslip_record.employee_id and payslip_record.employee_id.identification_id or '')
                    # previous cpf
                if previous_payslip_ids:
                    previous_payslip_record = payslip_obj.browse(cr, uid, previous_payslip_ids[0], context)    
                    if payslip_record.date_from != previous_payslip_record.date_from:
                        for previous_line in previous_payslip_record.line_ids:
                            if previous_line.register_id.name == 'CPF':
                                    p_cpf_amount += previous_line.amount

                # Counts Employee 
                if fwl_amount:
                    emp_fwl_amount += 1
                if cpf_amount != 0:
                    emp_cpf_amount += 1
                if mbmf_amount != 0:
                    emp_mbmf_amount += 1
                if sinda_amount != 0:
                    emp_sinda_amount += 1
                if cdac_amount != 0:
                    emp_cdac_amount += 1
                if ecf_amount != 0:
                    emp_ecf_amount += 1
                if cpfsdl_amount != 0:
                    emp_sdl_amount += 1
                
                # writes in xls file
                emp_flag = True
                sheet.write(raw_no, 4, round(cpf_amount or 0.00, 2), style)
                t_cpf_amount += cpf_amount
                total_cpf_amount += cpf_amount
                sheet.write(raw_no, 5, round(0.00, 2), style)
                sheet.write(raw_no, 8, round(mbmf_amount or 0.00, 2), style)
                t_mbmf_amount += mbmf_amount
                total_mbmf_amount += mbmf_amount
                sheet.write(raw_no, 9, round(sinda_amount or 0.00, 2), style)
                t_sinda_amount += sinda_amount
                total_sinda_amount += sinda_amount
                sheet.write(raw_no, 10, round(cdac_amount or 0.00, 2), style)
                t_cdac_amount += cdac_amount
                total_cdac_amount += cdac_amount
                sheet.write(raw_no, 11, round(ecf_amount or 0.00, 2), style)
                t_ecf_amount += ecf_amount
                total_ecf_amount += ecf_amount
                sheet.write(raw_no, 12, round(cpfsdl_amount or 0.00, 2), style)
                t_cpfsdl_amount += cpfsdl_amount
                total_cpfsdl_amount += cpfsdl_amount
                sheet.write(raw_no, 13, round(gross_amount or 0.00, 2), style)
                t_gross_amount += gross_amount
                total_gross_amount += gross_amount
                sheet.write(raw_no, 6, round(p_cpf_amount or 0.00, 2), style)
                t_p_cpf_amount += p_cpf_amount
                total_p_cpf_amount += p_cpf_amount
    
                sheet.write(raw_no, 14, 0.00, style)
                #sheet.write(raw_no, 6, 0.00, style)
                contract_id = hr_contract_obj.search(cr, uid, [('employee_id', '=', record.id), '|', ('date_end','>=', payslip_record.date_from),('date_end','=',False)])
                old_contract_id = hr_contract_obj.search(cr, uid, [('employee_id', '=', record.id), ('date_end','<=', payslip_record.date_from)])
                for contract in hr_contract_obj.browse(cr, uid, contract_id):
                    if payslip_record.employee_id.active == False:
                        sheet.write(raw_no, 7, 'Left')
                    elif contract.date_start >= payslip_record.date_from and not old_contract_id:
                        sheet.write(raw_no, 7, 'New Join')
                    else:
                        sheet.write(raw_no, 7, 'Existing')
                raw_no += 1
            
            if emp_flag:
                raw_no = raw_no + 1
                sheet.write(raw_no, 0, 'Total :' , bold_style)
                start_row = start_row + 1 
                
                sheet.write(raw_no, 4, round(total_cpf_amount or 0.00, 2), new_style)  # cpf
                sheet.write(raw_no, 5, round(0.00, 2), style)  # v_cpf
                sheet.write(raw_no, 6, round(total_p_cpf_amount or 0.00, 2), new_style)  # p_cpf
        
                sheet.write(raw_no, 8, round(total_mbmf_amount or 0.00, 2), new_style)  # MBPF
                sheet.write(raw_no, 9, round(total_sinda_amount or 0.00, 2), new_style)  # SINDA
                sheet.write(raw_no, 10, round(total_cdac_amount or 0.00, 2), new_style)  # CDAC
                sheet.write(raw_no, 11, round(total_ecf_amount or 0.00, 2), new_style)  # ECF
                sheet.write(raw_no, 12, round(total_cpfsdl_amount or 0.00, 2), new_style)  # ECF
                sheet.write(raw_no, 13, round(total_gross_amount or 0.00, 2), new_style)  # O_WAGE
                sheet.write(raw_no, 14, round(0.00, 2), style)
        
                raw_no = raw_no + 2
                start_row = start_row+ 3
        # amount columns 
        sheet.write(16, 8, round(t_cpf_amount or 0.00, 2), style)  # cpf
        sheet.write(17, 8, 0.00, style)
        sheet.write(18, 8, 0.00, style)
        sheet.write(19, 8, 0.00, style)
        sheet.write(20, 8, 0.00, style)
        sheet.write(21, 8, 0.00, style)
        sheet.write(22, 8, t_p_fwl_amount, style)
        sheet.write(23, 8, t_p_cpf_sdl_amount, style)
        sheet.write(24, 8, 0.00, style)
        sheet.write(25, 8, round(t_mbmf_amount or 0.00, 2), style)  # MBPF
        sheet.write(26, 8, round(t_sinda_amount or 0.00, 2), style)  # SINDA
        sheet.write(27, 8, round(t_cdac_amount or 0.00, 2), style)  # CDAC
        sheet.write(28, 8, round(t_ecf_amount or 0.00, 2), style)  # ECF
        
        # no of employee
        sheet.write(16, 10, emp_cpf_amount)
        sheet.write(17, 10, 0)
        sheet.write(18, 10, 0)
        sheet.write(19, 10, 0)
        sheet.write(20, 10, 0)
        sheet.write(21, 10, 0)
        sheet.write(22, 10, emp_fwl_amount)
        sheet.write(23, 10, emp_sdl_amount)
        sheet.write(24, 10, 0)
        sheet.write(25, 10, emp_mbmf_amount)  
        sheet.write(26, 10, emp_sinda_amount)
        sheet.write(27, 10, emp_cdac_amount)
        sheet.write(28, 10, emp_ecf_amount)
        
        sheet.write(30, 8, xlwt.Formula("sum(I17:I29)"), new_style)  # Total
        
        wbk.save(tempfile.gettempdir() + "/payslip.xls")
        
        file = open(tempfile.gettempdir() + "/payslip.xls", "rb")
        out = file.read()
        file.close()
        
        return base64.b64encode(out)
    
    def _get_file_name(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        if context is None: context = {}
        period_id = context.get('period_id')
        if not period_id:
            return ''
        period_data = period_obj.browse(cr, uid, period_id, context=context)
        end_date = datetime.strptime(period_data.date_stop, DEFAULT_SERVER_DATE_FORMAT)
        monthyear = end_date.strftime('%m%Y')
        file_name = "Payment Advice " + monthyear + '.xls'
        return file_name
    
    _defaults = {
         'name': _get_file_name,
         'xls_file': _print_report,
    }    
    
cpf_binary_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
