# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _
import random
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from dateutil.tz import tzlocal
from tzlocal import get_localzone
from openerp.addons.tgb_bez_balloons_report.report import amount_to_text_en
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'get_datenow': self.get_datenow,
            'convert_date_d_m_Y': self.convert_date_d_m_Y,
            'convert': self.convert,
            'convert_date': self.convert_date,
            'get_contact': self.get_contact,
            'get_jobs_person': self.get_jobs_person,
        })
        
    def get_datenow(self):
        return time.strftime('%d/%m/%Y')
    
    def convert_date_d_m_Y(self,date):
        if date:
            return datetime.strptime(date,'%Y-%m-%d').strftime('%d/%m/%Y')
        return ''
    
    def convert(self, amount):
        amount_text = amount_to_text_en.amount_to_text(amount, 'en', ' ')
        return amount_text.upper()
    
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
