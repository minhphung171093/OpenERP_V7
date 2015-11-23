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
from openerp import pooler
from openerp.report import report_sxw
from dateutil.parser import parse

class partner_statement_new(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(partner_statement_new, self).__init__(cr, uid, name, context=context)
        self.init_bal_sum = 0.0
        self.total = []
        self.headings = []
        self.headings = self._headings()
        self.localcontext.update( {
            'get_date':self._get_date,
            'time':time,
            'adr_get': self._adr_get,
            'lines': self._lines,
            'total': self._get_total,
            'initial': self._get_initial,
            'total_heading': self._get_headings,
        })
    def _get_date(self):
        return self.localcontext.get('datex')
    def _get_total(self, key):
        """
        Returns float value of list at position key
        @param key: an int
        """
        return self.total[key]

    def _get_initial(self):
        """
        @return: float initial balance
        """
        return self.init_bal_sum

    def _headings(self):
        """
        @return: a list of headings for aging
        """
        if self.localcontext['form']['aging'] == 'months':
            return ['Current', '1 Month', '2 Month', '3 Months +', 'Total']
        else:
            days = self.localcontext['form']['days']
            return [('0-'+str(days)+' days'), (str(days+1)+'-'+str(days*2)+' days'), str(days*2+1)+'-'+str(days*3)+' days', str(days*3+1)+' days+', 'Total']

    def _get_headings(self, key):
        """
        @return: value of list at position key
        @param key: an int
        """
        return self.headings[key]

    def _adr_get(self, partner, type):
        """
        @return: a res.partner.address browse record of partner and type
        @param partner: usually latest partner browse record - 'o'
        @param type: the type of address e.g. 'invoice'
        """
        res_partner = pooler.get_pool(self.cr.dbname).get('res.partner')
        addresses = res_partner.address_get(self.cr, self.uid, [partner.id], [type])
        if addresses:
            res_partner_address = pooler.get_pool(self.cr.dbname).get('res.partner.address').browse(self.cr, self.uid, [addresses[type]])
        return res_partner_address or False

    def _get_index(self, date, base_date):
        """
        This function provides an index for aging and inclusion purposes.
        @return: int which can be used to select/update an item in a list.
        @param date: the date of an invoice
        @param base_date: the date the report is based on
        """
        inv_date = parse(date)
        if self.localcontext['form']['aging'] == 'months':
            base_month = base_date.month
            base_year = base_date.year
            inv_month = inv_date.month
            inv_year = inv_date.year
            if base_year < inv_year: return 0
            if base_year > inv_year: base_month+=12*(base_year-inv_year)
            if inv_month > base_month: return 0
            return min((base_month - inv_month),3)
        else:
            days = self.localcontext['form']['days']
            delta = base_date-inv_date
            index = 0
            index = max(delta.days / days, 0)
            return min(index,3)

    def _lines(self, partner):
        """
        @return: list of dictionaries based on account.move.lines. To
        reduce search calls move_ids are calculated once in wizard and
        accessed via localcontext rather than param.
        @param partner: usually latest partner browse record - 'o'
        """
        self.total = [0.0 for i in range(5)]
        self.init_bal_sum = 0.0
        result = []
        ids = self.localcontext['move_ids'][str(partner.id)]
        move_line_pool = pooler.get_pool(self.cr.dbname).get('account.move.line')
        moves = move_line_pool.browse(self.cr, self.uid, ids)
        date = self.localcontext['datex']
        if not date:
            date = time.strftime('%Y-%m-%d')
        base_date = parse(date)

        for line in moves:
            if line.credit and line.reconcile_partial_id:
                continue
            if parse(line.date) > base_date:
                continue
            original_amount = line.credit or line.debit or 0.0
            amount_unreconciled = line.amount_residual_currency
            rs = {
                'name':line.move_id.name,
                'description': line.ref,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': line.credit and original_amount*-1 or original_amount,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': line.credit and amount_unreconciled*-1 or amount_unreconciled,
            }

            if self.localcontext['form']['statement_type'] == 'open' or self._get_index(line.date, base_date) == 0:
                result.append(rs)
            else:
                self.init_bal_sum+=rs['amount_unreconciled']
            self.total[4]+=rs['amount_unreconciled']
            self.total[self._get_index(line.date, base_date)]+=rs['amount_unreconciled']
            print 'result ',result
        return result
report_sxw.report_sxw('report.partner.statement.new', 'res.partner', 'addons/TGB_financial_report/report/partner_statement_new.rml', parser=partner_statement_new, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

