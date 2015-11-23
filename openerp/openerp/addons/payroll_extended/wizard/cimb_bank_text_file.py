# -*- coding: utf-8 -*-

from osv import osv, fields
import base64
import tempfile
from tools.translate import _
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
import tools

class cimb_bank_text_file(osv.osv_memory):

    _name = 'cimb.bank.text.file'

    _columns = {
        'source_account_number': fields.integer('Source Account Number', size=11),
        'account_name': fields.char('Account Name', size=100),
        'remark': fields.char('Remark', size=80),
        'transaction_date': fields.date('Transaction Date'),
        'period_id': fields.many2one('account.period', 'Period'),
    }

    def download_cimb_bank_txt_file(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])[0]
        context.update({'datas': data})
        return {
          'name': _('Binary'),
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'binary.cimb.bank.text.file.wizard',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
        }

cimb_bank_text_file()


class binary_cimb_bank_text_file_wizard(osv.osv_memory):

    _name = 'binary.cimb.bank.text.file.wizard'

    def _generate_cimb_bank_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        period_data = self.pool.get('account.period').browse(cr, uid, context.get('datas')['period_id'][0], context=context)
        start_date = period_data.date_start
        end_date = period_data.date_stop
        emp_ids = employee_obj.search(cr, uid, [('bank_detail_ids', '!=', False)], order="name", context = context)
        payslip_ids = payslip_obj.search(cr, uid, [('employee_id', 'in', emp_ids), ('cheque_number','=',False), ('date_from', '>=', start_date), ('date_from', '<=', end_date)], order="employee_name")
        if not payslip_ids:
            raise osv.except_osv(_('Error'), _('There is no payslip found to generate text file.'))
        tgz_tmp_filename = tempfile.mktemp('.' + "csv")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            net_amount_total=0.0
            detail_record = ''
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                if not payslip.employee_id.bank_detail_ids:
                    raise osv.except_osv(_('Error'), _('There is no bank detail found for %s .' % (payslip.employee_id.name) ))
                bank = payslip.employee_id.bank_detail_ids[0]
                bank_list = []
                if not bank.bank_ac_no:
                    bank_list.append('Bank Account Number')
                if not bank.branch_code:
                    bank_list.append('Branch Code')
                if not bank.bank_code:
                    bank_list.append('Bank Code')
                remaing_bank_detail = ''
                if bank_list:
                    for bank in bank_list:
                        remaing_bank_detail += tools.ustr(bank) + ', '
                    raise osv.except_osv(_('Error'), _('%s not found For %s Employee.' % (remaing_bank_detail, payslip.employee_id.name) ))
                net_amount = 0.0
                for line in payslip.line_ids:
                    if line.code == 'NET':
                        net_amount = line.total
                        net_amount_total += line.total
                net_amount = '%.2f' % net_amount
                detail_record += tools.ustr(bank.bank_ac_no)[:40] + \
                            ',' + tools.ustr(payslip.employee_id.name)[:100] + \
                            ',SGD'.ljust(4) + \
                            ',' + tools.ustr(net_amount)[:17] + \
                            ',' + tools.ustr(context.get('datas')['remark'] or '')[:80] + \
                            ',' + tools.ustr(bank.bank_code)[:40] + \
                            ',' + tools.ustr(bank.branch_code)[:40] + \
                            ',N'.ljust(2) + \
                            ''[:100] + "\r\n"
            net_amount_total = '%.2f' % net_amount_total
            transactiondate = datetime.datetime.strptime(context.get('datas')['transaction_date'], DEFAULT_SERVER_DATE_FORMAT)
            transactiondate = transactiondate.strftime('%Y%m%d')
            header_record = tools.ustr(context.get('datas')['source_account_number'])[:40] + \
                            ',' + tools.ustr(context.get('datas')['account_name'] or '')[:100] + \
                            ',SGD'.ljust(4) + \
                            ',' + tools.ustr(net_amount_total)[:17] + \
                            ',' + tools.ustr(context.get('datas')['remark'] or '')[:80] + \
                            ',' + tools.ustr(len(payslip_ids))[:5] + \
                            ',' + tools.ustr(transactiondate or '')[:8] + "\r\n"
            tmp_file.write(header_record)
            tmp_file.write(detail_record)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out)

    _columns = {
        'name': fields.char('Name', size=64),
        'cimb_bank_txt_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }

    _defaults = {
         'name': 'CIMB_Bank.csv',
         'cimb_bank_txt_file': _generate_cimb_bank_file,
    }

binary_cimb_bank_text_file_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
