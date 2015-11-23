# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime, timedelta

class TGB_birthday_alert_setting(osv.osv_memory):
    _name = 'tgb.birthday.alert'

    def test(self,cr,uid,ids):
        self.create_birthday_alert(cr,uid)

    def create_mail_message(self,cr,uid,partner_ids,message,day,user_ids=[]):
        if len(user_ids)>0:
            mail_message_obj = self.pool.get('mail.message')
            partner_list = "<p>"
            today = datetime.today()
            today = today.replace(hour=0,minute=0,second=0,microsecond=0)
            for partner in self.pool.get('res.partner').browse(cr,uid,partner_ids):
                partner_list+="</p><p>"+partner.name+""
                partner_birthday = datetime.strptime(partner.tgb_birthday+" 00:00:00","%Y-%m-%d %H:%M:%S")
                partner_birthday = partner_birthday.replace(year=today.year)
                coming_days = (partner_birthday - today).days
                if coming_days ==0:
                    partner_list += "'s birthday is today"
                else:
                    partner_list += "'s birthday is coming on %s days" %coming_days
            partner_list+="</p>"
            body = "<p>"+message+ "</p>" + partner_list

            new_message = mail_message_obj.create(cr,uid,{
                                                          'partner_ids':[(6, 0, user_ids)],
                                                          'subject':'Birthday notification in %s day' %day,
                                                          'body':body,
                                                          'type':'comment',
                                                         })
            for user_id in user_ids:
                new_notification_message = self.pool.get('mail.notification').create(cr,uid,{'partner_id':user_id,
                                                                                            'message_id':new_message})

    def create_birthday_alert(self,cr,uid):
        uid = 1
        self.pool.get('tgb.insurance.policy.alert').check_alert(cr,uid)
        setting_obj = self.pool.get('tgb.insurance.setting')
        day = setting_obj.search(cr,uid,[('key','=','birthday_day')])
        if day and len(day)>0:
            day = setting_obj.browse(cr,uid,day[0]).value
        message = setting_obj.search(cr,uid,[('key','=','birthday_message')])
        if message and len(message)>0:
            message = setting_obj.browse(cr,uid,message[0]).value
        user = setting_obj.search(cr,uid,[('key','=','birthday_user_alert')])
        user_ids = []

        if user and len(user)>0:
            user_list = setting_obj.browse(cr,uid,user[0]).value
            user_names = user_list.split(',')
            for user_name in user_names:
                user_id = self.pool.get('res.users').search(cr,uid,[('login','=',user_name.strip(' ').lower())])
                if user_id and len(user_id)>0:
                    user_ids.append(user_id[0])

        if len(user_ids)>0:
            user_partner_ids =[]
            for user_id in self.pool.get('res.users').browse(cr,uid,user_ids):
                if user_id.partner_id:
                    user_partner_ids.append(user_id.partner_id.id)
            today = datetime.today()
            next_date = (today + timedelta(days=int(day)))
            partner_ids=[]
            while today<=next_date:
                tday = today.day
                tmonth=today.month
                partner_ids.extend(self.pool.get('res.partner').search(cr,uid,[
                                                                          ('tgb_birthday_day','=',tday),
                                                                          ('tgb_birthday_month','=',tmonth),]))
                today = today+timedelta(days=1)
            if partner_ids and len(partner_ids)>0:
                return self.create_mail_message(cr,uid,partner_ids,message,day,user_partner_ids)
        return True
TGB_birthday_alert_setting()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

