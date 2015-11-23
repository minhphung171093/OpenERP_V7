# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime, date


class TGB_insurance_policy_alert(osv.osv):
    _name = 'tgb.insurance.policy.alert'

    def check_alert(self, cr, uid):
        today = date.today()
        today = today.strftime('%Y-%m-%d')
        # plan_detail_ids = self.pool.get('tgb.partner.plan.detail').search(cr,uid,[('date_of_alert','=',today)])
        # if plan_detail_ids and len(plan_detail_ids)>0:
        # partner_ids=[]
        #     for plan in self.pool.get('tgb.partner.plan.detail').browse(cr,uid,plan_detail_ids):
        #         partner = plan.partner_id
        #         policy_alert=" "
        #         if plan.plan_id.name:
        #             policy_alert = plan.plan_id.name
        #         self.pool.get('tgb.insurance.policy.alert').create(cr,1,{'partner_id':partner.id,
        #                                                                    'date_of_alert':plan.date_of_alert,
        #                                                                    'remark':plan.remark,
        #                                                                    'policy_alert':policy_alert})

        customer_policy_alert_ids = self.pool.get('tgb.customer.policy.alert').search(cr, uid,[('date_of_alert', '=', today)])
        if customer_policy_alert_ids and len(customer_policy_alert_ids) > 0:
            partner_ids = []
            for alert in self.pool.get('tgb.customer.policy.alert').browse(cr, uid, customer_policy_alert_ids):
                partner = alert.partner_id
                self.pool.get('tgb.insurance.policy.alert').create(cr, 1, {'partner_id': partner.id,
                                                                           'date_of_alert': alert.date_of_alert,
                                                                           'remark': alert.remark,
                })
                self.create_mail_message(cr,1,partner.id,alert.remark)

    def create_mail_message(self,cr,uid,partner_id,message,user_ids=[]):
        user_ids = [3]
        if len(user_ids)>0:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            mail_message_obj = self.pool.get('mail.message')
            body = "<p>"+message+ "</p>"
            new_message = mail_message_obj.create(cr,uid,{
                                                          'partner_ids':[(6, 0, user_ids)],
                                                          'subject':'Policy Alert of %s' %partner.name,
                                                          'body':body,
                                                          'type':'comment',
                                                         })
            print 'why not new mail message'
            for user_id in user_ids:
                new_notification_message = self.pool.get('mail.notification').create(cr,uid,{'partner_id':user_id,
                                                                                            'message_id':new_message})

    def test(self,cr,uid,ids,context={}):
        self.check_alert(cr,uid)

    _columns = {
        'partner_id':fields.many2one('res.partner',required=True,string="Customer"),
        'date_of_alert': fields.date('Date of Alert', required=True),
        'remark': fields.char('Remarks', size=256, select=1, required=True),
    }
    _sql_constraints = [
        ('key_uniq', 'unique (key)', 'Key must be unique.')
    ]
    _order = 'date_of_alert desc'


TGB_insurance_policy_alert()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

