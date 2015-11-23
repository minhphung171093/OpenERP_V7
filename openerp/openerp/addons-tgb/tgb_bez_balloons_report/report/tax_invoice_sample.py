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
class tax_invoice_sample(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(tax_invoice_sample, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_date': self.convert_date,
            'get_contact': self.get_contact,
            'get_do': self.get_do,
            'get_jobs_person': self.get_jobs_person,
        })

    def convert_date(self,date):
        date = datetime.strptime(date, '%Y-%m-%d')
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
    
    def get_do(self,origin):
        res = ''
        if origin:
            do = origin.split(':')
            if len(do)>=2:
                res=do[0]
        return res
        
    def get_jobs_person(self, origin):
        res = ''
        if origin:
            so = origin.split(':')
            if len(so)==1:
                sql = '''
                    select name from res_partner where id in (select partner_id from res_users where id in (select user_id from sale_order where name='%s'))
                '''%(so[0])
            else:
                sql = '''
                    select name from res_partner where id in (select partner_id from res_users where id in (select user_id from sale_order where name='%s'))
                '''%(so[1])
            self.cr.execute(sql)
            name = self.cr.fetchone()
            res = name and name[0] or ''
        return res
        
report_sxw.report_sxw('report.tax_invoice_sample', 'account.invoice', 'addons/tgb_bez_balloons_report/report/tax_invoice_sample.rml', parser=tax_invoice_sample, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

