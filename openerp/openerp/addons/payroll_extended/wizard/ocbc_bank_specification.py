from osv import osv, fields
import base64
import tempfile
import time
from tools.translate import _
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT

t_codes=[
    ('20', _('20 - Sundry Credit')),
    ('21', _('21 - Standing Instruction')),
    ('22', _('22 - Salary Credit')),
    ('23', _('23 - Dividend')),
    ('24', _('24 - Inward Remittance')),
    ('25', _('25 - Proceeds of Bill')),
    ('30', _('30 - Direct Debit'))
]

class binary_ocbc_bank_file_wizard(osv.osv_memory):

    _name = 'binary.ocbc.bank.file.wizard'

    _columns = {
        'name': fields.char('Name', size=64),
        'cpf_txt_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }

    def _generate_file(self, cr, uid, context = None):
        tgz_tmp_filename = tempfile.mktemp('.'+"txt")
        tmp_file = open(tgz_tmp_filename, "wr")
        try:
            period_obj = self.pool.get("account.period")
            payslip_obj = self.pool.get("hr.payslip")
            if not context.get("month"):
                return False
            period_rec = period_obj.browse(cr, uid, context.get("month"), context = context)
            current_date = datetime.datetime.today()
            year_month_date = current_date.strftime('%Y%m%d')
            
            header2_record = ''
            header1_record = 'OVERSEA-CHINESE BANKING CORP GROUP'.ljust(34)+ \
                            ''.ljust(24)+ \
                            '&&&&&&&&&&&&&&&&&&&&&&&&'.ljust(24) +\
                            '\r\n'
#                            ljust(len(split_total_rule.split('.')[0])+3, '0')
            tmp_file.write(header1_record)
            header2_record += ('%03d' % context.get('branch_number')).ljust(3)
            header2_record += ('%09d' % context.get('account_number')).ljust(9)
            header2_record += year_month_date.ljust(8)
            header2_record += ('%03d' % context.get('batch_number')).ljust(3)
            company_name = context.get("company_name", '')
            if company_name.__len__() <= 20:
                company_name = company_name.ljust(20)
            else:
                company_name = company_name[0:20].ljust(20)
            header2_record += company_name

            value_date = datetime.datetime.strptime(context.get("value_date"), "%Y-%m-%d")
            header2_record += value_date.strftime('%Y%m%d').ljust(8) + ''.ljust(31) 
            header2_record += '\r\n'
            tmp_file.write(header2_record)
            employe_obj = self.pool.get("hr.employee")
            emp_ids = employe_obj.search(cr, uid, [('bank_detail_ids', '!=', False)], order="name", context = context)
            serial_number = 50000
            payment_detail = ''
            for employee in employe_obj.browse(cr, uid, emp_ids, context = context):
                if not employee.bank_detail_ids:
                    continue
                payslip_id = payslip_obj.search(cr, uid, [('employee_id', '=', employee.id), ('cheque_number','=',False), ('date_from', '>=', period_rec.date_start), ('date_to', '<=', period_rec.date_stop)])
                if not payslip_id:
                    continue
                if serial_number == 99999:
                    serial_number = 50001
                payment_detail += str(serial_number).ljust(5)
                bank_code = employee.bank_detail_ids[0].bank_code and employee.bank_detail_ids[0].bank_code or ''
                if bank_code.__len__() <= 4:
                    payment_detail += bank_code.rjust(4, '0')
                else:
                    payment_detail += bank_code[0:4].ljust(4)
                emp_branch_code = employee.bank_detail_ids[0].branch_code and employee.bank_detail_ids[0].branch_code or ''
                if emp_branch_code.__len__() <= 3:
                    payment_detail += emp_branch_code.rjust(3, '0')
                else:
                    payment_detail += emp_branch_code[0:3].ljust(3)
                emp_bank_ac_no = employee.bank_detail_ids[0].bank_ac_no and employee.bank_detail_ids[0].bank_ac_no or ''
                if emp_bank_ac_no.__len__() <= 11:
                    payment_detail += emp_bank_ac_no.ljust(11, ' ')
                else:
                    payment_detail += emp_bank_ac_no[0:11].ljust(11)
                emp_bank_name = employee.bank_detail_ids[0].beneficiary_name and employee.bank_detail_ids[0].beneficiary_name or ''
                if emp_bank_name:
                    if emp_bank_name.__len__() <= 20:
                        payment_detail += emp_bank_name.ljust(20)
                    else:
                        payment_detail += emp_bank_name[0:20].ljust(20)
                else:
                    if employee.name.__len__() <= 20:
                        payment_detail += employee.name.ljust(20)
                    else:
                        payment_detail += employee.name[0:20].ljust(20)
                payment_detail += context.get('transaction_code').ljust(2)
                payment_detail += ''.ljust(24)
                total_amout = 0
                for line in payslip_obj.browse(cr, uid, payslip_id[0]).line_ids:
                    if line.code == "NET":
                        total_amout = line.amount
                if total_amout:
                    total_amout = total_amout * 100
                    total_amout = int(round(total_amout))
                    payment_detail += ('%011d' % total_amout).ljust(11)
                else:
                    payment_detail += ('%011d' % 0).ljust(11)
                payment_detail += "".ljust(2)
                payment_detail += '\r\n'
                serial_number +=1;
            tmp_file.write(payment_detail)
        finally:
            tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out) 

    def _get_file_name(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        period_id = context.get('month')
        if not period_id:
            return 'ocbc_txt_file.txt'
        period_data = period_obj.browse(cr, uid, period_id, context=context)
        end_date = datetime.datetime.strptime(period_data.date_stop, DEFAULT_SERVER_DATE_FORMAT)
        monthyear = end_date.strftime('%b%Y')
        file_name = 'ocbc_txt_file_' + monthyear + '.txt'
        return file_name

    _defaults = {
                 'name': _get_file_name,
                 'cpf_txt_file': _generate_file,
    }
binary_ocbc_bank_file_wizard()

class ocbc_bank_specification(osv.osv_memory):
    
    _name = 'ocbc.bank.specification'

    def create(self, cr, uid, vals, context=None):
        if vals and vals.get('branch_number') and len(str(vals.get('branch_number'))) > 3:
            raise osv.except_osv(_('Error'), _('Branch number length must be less than or equal to three digits.'))
        if vals and vals.get('batch_number') and len(str(vals.get('batch_number'))) > 3:
            raise osv.except_osv(_('Error'), _('Batch number length must be less than or equal to three digits.'))
        if vals and vals.get('account_number') and len(str(vals.get('account_number'))) > 9:
            raise osv.except_osv(_('Error'), _('Account number length must be less than or equal to nine digits.'))
        return super(ocbc_bank_specification, self).create(cr, uid, vals, context)

    _columns = {
                'branch_number': fields.integer('Branch Number', size=3, required=True),
                'batch_number': fields.integer('Batch Number', size=3, required=True),
                'account_number': fields.integer('Account Number', size=9, required=True),
                'month': fields.many2one('account.period', 'Month', required=True),
                'value_date':fields.date("Value Date", required=True),
                'transaction_code': fields.selection(t_codes,'Transaction Code', required=True,size=2),
    }
    _defaults = {
         "value_date": lambda *a:datetime.datetime.now().strftime('%Y-%m-%d')
    }
    def get_text_file(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])[0]
        context.update({'branch_number': data.get('branch_number'), 'account_number': data.get("account_number"),
                        'month': data.get("month")[0],'value_date': data.get("value_date"), 'batch_number': data.get("batch_number"),
                        'transaction_code': data.get("transaction_code")})
        user_data = self.pool.get("res.users").browse(cr, uid, uid, context = context)
        context.update({'company_name': user_data.company_id.name})
        return {
              'name': _('Text file'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'binary.ocbc.bank.file.wizard',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context
        }
ocbc_bank_specification()