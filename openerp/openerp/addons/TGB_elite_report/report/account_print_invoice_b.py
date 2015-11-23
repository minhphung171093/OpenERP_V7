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
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
class account_invoiceb(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoiceb, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
            'type':self.type,
            'get_tax_percent':self._get_tax_percent,})
    def type(self):
        return 'b'
    def _get_tax_percent(self, invoice):
        amount_untaxed = invoice.amount_untaxed
        amount_tax = invoice.amount_tax
        percent = round(amount_tax/amount_untaxed * 100,2)
        return percent
    def convert(self, amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount, 'en', cur)
        return amt_en
report_sxw.report_sxw(
    'report.tgb.account.invoiceb',
    'account.invoice',
    'addons/TGB_elite_report/report/account_print_invoice.rml',
    parser=account_invoiceb
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
