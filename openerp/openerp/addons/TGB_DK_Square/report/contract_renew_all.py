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

class contract_renew_all(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(contract_renew_all, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'period_name_get':self._period_name_get,
        })

    def _period_name_get(self,code, context=None):
        period = code.split('/')
        mon = period[0]
        name=''
        if period[0]=='01':
            mon="JAN'"
        elif period[0]=='02':
            mon="FEB'"
        elif period[0]=='03':
            mon="MAR'"
        elif period[0]=='04':
            mon="APR'"
        elif period[0]=='05':
            mon="MAY'"
        elif period[0]=='06':
            mon="JUN'"
        elif period[0]=='07':
            mon="JUL'"
        elif period[0]=='08':
            mon="AUG'"
        elif period[0]=='09':
            mon="SEP'"
        elif period[0]=='10':
            mon="OCT'"
        elif period[0]=='11':
            mon="NOV'"
        elif period[0]=='12':
            mon="DEC'"
        name = mon+period[1][-2:]
        return name


report_sxw.report_sxw('report.dk.contract.renew.all', 'dk.contract', 'addons/TGB_DK_Square/report/contract_renew_all.rml', parser=contract_renew_all, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

