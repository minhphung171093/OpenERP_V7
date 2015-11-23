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


class account_invoice_TGB(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_TGB, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_taxes': self._get_taxes,
            'upper':self._upper,
            'get_type':self._get_type,
            'display_supplier_address':self._display_supplier_address,
            'get_delivery_order':self._get_delivery_order,
        })
    def _get_delivery_order(self,o):
        order_origins = o.origin
        stock_picking_ids  = self.pool.get('stock.picking').search(self.cr,self.uid,[('origin','=',order_origins)])
        returnPO = ''
        for picking in self.pool.get('stock.picking').browse(self.cr,self.uid,stock_picking_ids):
            returnPO += picking.name+ ' /'
        return returnPO[:-1]

    def _display_supplier_address(self,o):
        address = ''
        if o.street:
            address+=o.street+', '
        if o.street2:
            address+=o.street2+', '
        if o.city:
            address+=o.city+', '
        if o.state_id:
            address+=o.state_id.name+', '
        if o.zip:
            address+=o.zip+', '
        if o.country_id:
            address+=o.country_id.name
        return address
    def _get_type(self,o):
        if o.type=='out_invoice':
            return 1
        elif o.type=='in_invoice':
            return 2
        else:
            return 3

    def _get_taxes(self, o):
        taxes = ''
        for invoice_line in o.invoice_line:
            for tax in invoice_line.invoice_line_tax_id:
                if tax.name:
                    if tax.type == 'percent':
                        taxes = taxes + tax.name + ' '+ str(tax.amount * 100) + '% ,'
                    else:
                        taxes = taxes + tax.name + ' '+ str(tax.amount) + ', '
        taxes = taxes[:-1]
        return taxes

    def _upper(self, s):
            if type(s) == type(u""):
                return s.upper()
            return '%' + unicode(s, "utf8").upper().encode("utf8") + '%'


report_sxw.report_sxw(
    'report.account.invoice.TGB',
    'account.invoice',
    'addons/TGB_account/report/TGB_account_print_invoice.rml',
    parser=account_invoice_TGB
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
