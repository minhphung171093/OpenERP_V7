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
from datetime import datetime
class delivery_order_sample(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(delivery_order_sample, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_date': self.convert_date,
            'get_contact': self.get_contact,
            'get_invoice': self.get_invoice,
        })

    def convert_date(self,date):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return date.strftime('%d-%b-%y (%a)')
        
    def get_contact(self,partner_id):
        vals = {
            'name': '',
            'tel': '',
            'fax': '',
            'hp': '',
            'email': '',
        }
        if partner_id and partner_id.child_ids:
            contact = partner_id.child_ids[0]
            vals = {
                'name': contact.name,
                'tel': contact.phone,
                'fax': contact.fax,
                'hp': contact.hp,
                'email': contact.email,
            }
        return vals
    
    def get_invoice(self,name):
        sql = '''
            select number from account_invoice where origin like'%'''+name+'''%' limit 1
        '''
        self.cr.execute(sql)
        invoice = self.cr.fetchone()
        return invoice and invoice[0] or ''
    
report_sxw.report_sxw('report.delivery_order_sample', 'stock.picking.out', 'addons/tgb_bez_balloons_report/report/delivery_order_sample.rml', parser=delivery_order_sample, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

