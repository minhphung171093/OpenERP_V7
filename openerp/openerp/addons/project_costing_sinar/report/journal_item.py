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

class journal(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(journal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_credit_sum': self.get_credit_sum,
            'get_debit_sum': self.get_debit_sum,
        })
    def get_credit_sum(self, line_ids):
        sum = 0.0
        for data in line_ids:
            sum = sum + data.credit
        return sum
    
    def get_debit_sum(self, line_ids):
        sum = 0.0
        for data in line_ids:
            sum = sum + data.debit
        return sum
    
report_sxw.report_sxw('report.account.move.line', 'account.move.line', 'addons/project_costing_sinar/report/journal_item.rml', parser=journal, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

