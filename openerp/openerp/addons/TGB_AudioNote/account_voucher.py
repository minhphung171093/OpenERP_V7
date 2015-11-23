# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def create(self, cr, uid, vals, context={}):
        print 'context in create', context
        if context.get('create_fields'):
            fields_list = ['comment', 'line_cr_ids', 'is_multi_currency', 'reference', 'line_dr_ids', 'company_id', 'currency_id', 'narration', 'partner_id', 'payment_rate_currency_id', 'paid_amount_in_company_currency', 'writeoff_acc_id', 'state', 'pre_line', 'type', 'payment_option', 'account_id', 'period_id', 'date', 'payment_rate', 'name', 'writeoff_amount', 'analytic_id', 'journal_id', 'amount']
            values = self.default_get(cr,uid,fields_list,context)
            line_cr_ids = []
            if values.get('comment', False):
                vals.update({'comment':values.get('comment')})
            if values.get('line_cr_ids', False):
                line_cr_ids = values.get('line_cr_ids')
                vals.update({'line_cr_ids':line_cr_ids})
            if values.get('is_multi_currency', False):
                vals.update({'is_multi_currency':values.get('is_multi_currency')})
            if values.get('reference', False):
                vals.update({'reference':values.get('reference')})
            if values.get('line_dr_ids', False):
                vals.update({'line_dr_ids':values.get('line_dr_ids')})
            company_id = None
            if values.get('company_id', False):
                company_id = values.get('company_id')
                vals.update({'company_id':company_id})
            if values.get('currency_id', False):
                vals.update({'currency_id':values.get('currency_id')})
            if values.get('narration', False):
                vals.update({'narration':values.get('narration')})
            if values.get('partner_id', False):
                vals.update({'partner_id':values.get('partner_id')})
            if values.get('payment_rate_currency_id', False):
                vals.update({'payment_rate_currency_id':values.get('payment_rate_currency_id')})
            if values.get('paid_amount_in_company_currency', False):
                vals.update({'paid_amount_in_company_currency':values.get('paid_amount_in_company_currency')})
            if values.get('writeoff_acc_id', False):
                vals.update({'writeoff_acc_id':values.get('writeoff_acc_id')})
            if values.get('state', False):
                vals.update({'state':values.get('state')})
            if values.get('pre_line', False):
                vals.update({'pre_line':values.get('pre_line')})
            if values.get('type', False):
                vals.update({'type':values.get('type')})
            if values.get('payment_option', False):
                vals.update({'payment_option':values.get('payment_option')})
            if values.get('account_id', False):
                vals.update({'account_id':values.get('account_id')})
            if values.get('period_id', False):
                vals.update({'period_id':values.get('period_id')})
            date = None
            if values.get('date', False):
                date = values.get('date')
                vals.update({'date':date})
            if values.get('payment_rate', False):
                vals.update({'payment_rate':values.get('payment_rate')})
            if values.get('name', False):
                vals.update({'name':values.get('name')})
            if values.get('writeoff_amount', False):
                vals.update({'writeoff_amount':values.get('writeoff_amount')})
            if values.get('analytic_id', False):
                vals.update({'analytic_id':values.get('analytic_id')})
            amount = 0
            if values.get('amount', False):
                amount = values.get('amount')
                vals.update({'amount':amount})
            if values.get('journal_id', False):
                journal_id = values.get('journal_id')
                partner_id = values.get('partner_id',False)
                line_ids = False
                tax_id=False
                partner_pool = self.pool.get('res.partner')
                journal_pool = self.pool.get('account.journal')
                journal = journal_pool.browse(cr, uid, journal_id, context=context)
                partner = partner_pool.browse(cr, uid, partner_id, context=context)
                account_id = False
                tr_type = False
                if journal.type in ('sale','sale_refund'):
                    account_id = partner.property_account_receivable.id
                    tr_type = 'sale'
                elif journal.type in ('purchase', 'purchase_refund','expense'):
                    account_id = partner.property_account_payable.id
                    tr_type = 'purchase'
                else:
                    if not journal.default_credit_account_id or not journal.default_debit_account_id:
                        raise osv.except_osv(_('Error!'), _('Please define default credit/debit accounts on the journal "%s".') % (journal.name))
                    account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
                    tr_type = 'receipt'

                vals_get = self.onchange_journal(cr,uid,None,journal_id, line_cr_ids, False, partner_id, date, amount, type, company_id, context)['value']
                vals.update({'account_id': account_id})
                vals.update({'journal_id':values.get('journal_id')})
                vals.update(vals_get)

            line_cr_ids = vals.get('line_cr_ids')
            line_dr_ids = vals.get('line_dr_ids')

            if line_cr_ids:
                vals.pop('line_cr_ids')
            if line_dr_ids:
                vals.pop('line_dr_ids')
            voucher_id = super(account_voucher, self).create(cr, uid, vals, context)

            account_voucher_line_obj = self.pool.get('account.voucher.line')
            if line_cr_ids and len(line_cr_ids)>0:
                for lcr in line_cr_ids:
                    lcr.update({'voucher_id':voucher_id})
                    print 'cr ',lcr
                    account_voucher_line_obj.create(cr,uid,lcr)
            if line_dr_ids and len(line_dr_ids)>0:
                for ldr in line_dr_ids:
                    ldr.update({'voucher_id':voucher_id})
                    account_voucher_line_obj.create(cr,uid,ldr)
            return voucher_id
        else:
            return super(account_voucher, self).create(cr, uid, vals, context)

    def button_proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        wf_service = netsvc.LocalService("workflow")
        for vid in ids:
            wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        return {'type': 'ir.actions.act_window_close'}


    def default_get(self, cr, user, fields_list, context=None):
        values = super(account_voucher, self).default_get(cr, user, fields_list, context)
        if context.get('journal_id', False):
            values.update({'journal_id':context.get('journal_id')})
        if context.get('memo',False):
            values.update({'name':context.get('memo')})
        print 'values default get',values
        return values

    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        print 'voucher.line_ids',voucher.line_ids
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            move_line['tgb_payment_fee'] = voucher.tgb_payment_fee

            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)

    def action_move_line_create(self, cr, uid, ids, context=None):
        print 'check in account_move_line_Create'
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            print 'voucher here', voucher
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
            print 'rec_list_ids line total',rec_list_ids,line_total
            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True

    _columns={
        'tgb_payment_fee':fields.float('Payment Fee',digits_compute=dp.get_precision('Account'), ),
    }
    _defaults={
        'tgb_payment_fee':0,
    }
account_voucher()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
