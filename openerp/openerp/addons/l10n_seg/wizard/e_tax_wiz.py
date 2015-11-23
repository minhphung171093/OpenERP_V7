# -*- coding: utf-8 -*-

from osv import osv, fields
import base64
import tempfile
from tools.translate import _
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
from time import gmtime, strftime
import tools
import time

class e_tax_wiz(osv.osv):

    _name = 'e.tax.wiz'


    _columns = {
            'year_id': fields.many2one('account.fiscalyear', 'Year', required=True),
    }

    def download_e_tax_txt_file(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        context.update({'year_id': data['year_id'], 'datas': data})
        return {
          'name': _('Binary'),
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'binary.e.tax.text.file.wizard',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
        }


class binary_e_tax_text_file_wizard(osv.osv_memory):
    _name = 'binary.e.tax.text.file.wizard'

    def _generate_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        period_id = []
        if context and context.get('year_id'):
            period_id.append(context.get('year_id')[0])
        start_date = end_date = False
        if period_id:
            period_data = self.pool.get('account.fiscalyear').browse(cr, uid, period_id[0])
            start_date = period_data.date_start
            end_date = period_data.date_stop
        company_data = res_users_obj.browse(cr, uid, uid).company_id
        purchase_order_obj = self.pool.get('purchase.order')
        acc_invoice_obj = self.pool.get('account.invoice')
        tax_obj = self.pool.get('account.tax')
        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        customer_invoice_ids = acc_invoice_obj.search(cr, uid, [('state','not in',['draft']), ('partner_id.customer', '=', True), ('date_invoice', '>=', start_date), ('date_invoice', '<=', end_date)])
        supplier_invoice_ids = acc_invoice_obj.search(cr, uid, [('partner_id.supplier', '=', True), ('date_invoice', '>=', start_date), ('date_invoice', '<=', end_date)])
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            company_record = tools.ustr('CompInfoStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('CompanyName|CompanyUEN|GSTNo|PeriodStart|PeriodEnd|IAFCreationDate|ProductVersion|IAFVersion||||||') + \
                            "\r\n" + \
                            tools.ustr(company_data and company_data.name or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.company_uen or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.gst_no or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.period_start and datetime.datetime.strptime(company_data.period_start, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.period_end and datetime.datetime.strptime(company_data.period_end, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.iaf_creation_date and datetime.datetime.strptime(company_data.iaf_creation_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.product_version or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.iaf_version or '') + \
                            '|'.ljust(1) + \
                            "\r\n" + \
                            tools.ustr('CompInfoEnd|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                             tools.ustr('PurcDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('SupplierName|SupplierUEN|InvoiceDate|InvoiceNo|PermitNo|LineNo|ProductDescription|PurchaseValueSGD|GSTValueSGD|TaxCode|FCYCode|PurchaseFCY|GSTFCY| ') + \
                            "\r\n"
            tmp_file.write(company_record)
            
            for supplier in acc_invoice_obj.browse(cr, uid, supplier_invoice_ids):
                line_no = 1
                for line in supplier.invoice_line:
                    for tax in line.invoice_line_tax_id:
                        tax_amt = tax_amt_foreign = 0.0
                        tax_name = ''
                        tax_data = tax_obj.compute_all(cr, uid, [tax], (line.base_price * (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, supplier.partner_id)['taxes']
                        tax_data_foreign = tax_obj.compute_all(cr, uid, [tax], (line.price_unit * (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, supplier.partner_id)['taxes']
                        if tax_data:
                            tax_amt = tax_data[0]['amount']
                            tax_name = tax_data[0]['name']
                        if tax_data_foreign:
                            tax_amt_foreign = tax_data[0]['amount']
                        supplier_record = tools.ustr(supplier.partner_id.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(supplier.partner_id.supplier_uen or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(supplier and supplier.date_invoice and datetime.datetime.strptime(supplier.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(supplier.number or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(supplier.permit_no or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line_no or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(float(line.base_price * line.quantity) or 0.0) + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_amt or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(supplier.currency_id.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line.price_unit or 0.0) + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_amt_foreign or 0.0) + \
                                          '|'.ljust(1) + \
                                          "\r\n"
                        tmp_file.write(supplier_record)
                        line_no += 1
            customer_data = tools.ustr('PurcDataEnd|1402700|81725|10||||||||||') + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('SuppDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('CustomerName|CustomerUEN|InvoiceDate|InvoiceNo|LineNo|ProductDescription|SupplyValueSGD|GSTValueSGD|TaxCode|Country|FCYCode|SupplyFCY|GSTFCY|') + \
                            "\r\n"
            tmp_file.write(customer_data)
            
            for customer in acc_invoice_obj.browse(cr, uid, customer_invoice_ids):
                line_no = 1
                for line in customer.invoice_line:
                    for tax in line.invoice_line_tax_id:
                        tax_amt = tax_amt_foreign = 0.0
                        tax_name = ''
                        tax_data = tax_obj.compute_all(cr, uid, [tax], (line.base_price * (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, supplier.partner_id)['taxes']
                        tax_data_foreign = tax_obj.compute_all(cr, uid, [tax], (line.price_unit * (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, supplier.partner_id)['taxes']
                        if tax_data:
                            tax_amt = tax_data[0]['amount']
                            tax_name = tax_data[0]['name']
                        if tax_data_foreign:
                            tax_amt_foreign = tax_data[0]['amount']
                        supplier_record = tools.ustr(customer.partner_id.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer.partner_id.supplier_uen or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer and customer.date_invoice and datetime.datetime.strptime(customer.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer.number or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer.permit_no or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line_no or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(float(line.base_price * line.quantity) or 0.0) + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_amt or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer.partner_id.city or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(customer.currency_id.name or '') + \
                                          '|'.ljust(1) + \
                                          tools.ustr(line.price_unit or 0.0) + \
                                          '|'.ljust(1) + \
                                          tools.ustr(tax_amt_foreign or 0.0) + \
                                          '|'.ljust(1) + \
                                          "\r\n"
                        tmp_file.write(supplier_record)
                        line_no += 1
        
            account_data = tools.ustr('SuppDataEnd|30300|975.1|8||||||||||') + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('GLDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('TransactionDate|AccountID|AccountName|TransactionDescription|Name|TransactionID|SourceDocumentID|SourceType|Debit|Credit|Balance|||') + \
                            "\r\n"
            tmp_file.write(account_data)
            
            
            journal_ids = journal_obj.search(cr, uid, [])
            for journal in journal_obj.browse(cr, uid, journal_ids):
                move_ids = move_obj.search(cr, uid, [('journal_id','=',journal.id), ('date', '>=', start_date), ('date', '<=', end_date)])
                debit = credit = balance = 0.0
                cr.execute('SELECT SUM(debit),SUM(credit),SUM(debit-credit) FROM account_move_line WHERE id IN (SELECT move_id FROM account_analytic_line WHERE (date=%s) AND (journal_id=%s) AND (move_id is not null))', (start_date, journal.id,))
                for c in cr.fetchone():
                    debit = float(c or 0.0)
                    credit = float(c or 0.0)
                    balance = float(c or 0.0)
                opening_balance = tools.ustr(datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                  '|'.ljust(1) + \
                                  tools.ustr(journal.default_debit_account_id.code) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(journal.name) + \
                                  '|'.ljust(1) + \
                                  tools.ustr('OPENING BALANCE') + \
                                  '|||||'.ljust(1) + \
                                  tools.ustr(debit or 0.0) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(credit or 0.0) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(balance or 0.0) + \
                                  '|||'.ljust(1) + \
                                  "\r\n"
                tmp_file.write(opening_balance)
                for move in move_obj.browse(cr, uid, move_ids):
                    for line in move.line_id:
                        move_data = tools.ustr(move and move.date and datetime.datetime.strptime(move.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.account_id.code) + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.account_id.name) + \
                                    '|'.ljust(1) + \
                                    tools.ustr(move.ref or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.name or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(move.id or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.invoice.name or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.account_id.type or '') + \
                                    '|'.ljust(1) + \
                                    tools.ustr(float(line.debit) or 0.0 ) + \
                                    '|'.ljust(1) + \
                                    tools.ustr(float(line.credit) or 0.0 ) + \
                                    '|'.ljust(1) + \
                                    tools.ustr(line.amount_currency or 0.0) + \
                                    '|'.ljust(1) + \
                                    "\r\n"
                        tmp_file.write(move_data)
        
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out)


    _columns = {
        'name': fields.char('Name', size=64),
        'etax_txt_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }

    _defaults = {
         'name': 'ETAX.txt',
         'etax_txt_file': _generate_file,
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
