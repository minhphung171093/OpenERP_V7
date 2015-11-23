# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    def test(self,cr,uid,ids,context):
        self.pool.get('tgb.birthday.alert').create_birthday_alert(cr,uid)
    def _get_birthday_detail(self,cr,uid,ids,a,b,context={}):
        val={}
        for partner in self.browse(cr,uid,ids):
            val[partner.id]={}
            val[partner.id]['tgb_birthday_month'] = 0
            val[partner.id]['tgb_birthday_day'] = 0
            if partner.tgb_birthday:
                partner_birthday = datetime.strptime(partner.tgb_birthday,"%Y-%m-%d")
                val[partner.id]['tgb_birthday_month'] = str(partner_birthday.month)
                val[partner.id]['tgb_birthday_day'] = str(partner_birthday.day)
        return val

    def _get_tgb_insurance_detail(self,cr,uid,ids,a,b,context={}):
        val = {}
        for partner in self.browse(cr,uid,ids):
            val[partner.id]={}
            death_benefit = 0
            total_permanent_disability =0
            critical_illness=0
            accident_cover=0
            maturity_value=0
            yearly_premium =0
            monthly_premium=0
            early_crisis=0
            medical_reimbursement=0
            for plan in partner.plan_ids:
                death_benefit+=plan.death_benefit
                total_permanent_disability+=plan.total_permanent_disability
                critical_illness+=plan.critical_illness
                accident_cover+=plan.accident_cover
                maturity_value+=plan.maturity_value
                yearly_premium+=plan.yearly_premium
                monthly_premium+=plan.monthly_premium
                early_crisis+=plan.early_crisis
                medical_reimbursement+=plan.medical_reimbursement
            val[partner.id]={'death_benefit':death_benefit,
                             'total_permanent_disability':total_permanent_disability,
                             'critical_illness':critical_illness,
                             'accident_cover':accident_cover,
                             'maturity_value':maturity_value,
                             'yearly_premium':yearly_premium,
                             'monthly_premium':monthly_premium,
                             'early_crisis':early_crisis,
                             'medical_reimbursement':medical_reimbursement,
                            }
        return val


    def _get_customer_policy_alert_ids(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [('partner_id', 'child_of', ids)], context=context)

    _columns = {
        'insurance_parent_id':fields.many2one('res.partner','Insurance parent partner'),
        'insurance_depend_ids':fields.one2many('res.partner','insurance_parent_id','Partner Dependent'),
        'plan_ids': fields.one2many('tgb.partner.plan.detail','partner_id','Plan Purchase'),
        'customer_policy_alert_ids': fields.one2many('tgb.customer.policy.alert','partner_id','Policy Alert'),

        'death_benefit':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Death Benefit', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['death_benefit'], 10),}),

        'total_permanent_disability':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Total Permanent Disability', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['total_permanent_disability'], 10),}),

        'critical_illness':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Critical Illness', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['critical_illness'], 10),}),

        'accident_cover':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Accident Cover', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['accident_cover'], 10),}),

        'maturity_value':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Maturity Value', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['maturity_value'], 10),}),
        'yearly_premium':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Yearly Premium', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['yearly_premium'], 10),}),
        'monthly_premium':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Monthly Premium', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['monthly_premium'], 10),}),

        'early_crisis':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Early Crisis', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['early_crisis'], 10),}),

        'medical_reimbursement':fields.function(_get_tgb_insurance_detail,type='float',digits=(16,0), string='Medical Reimbursement', multi='tgb_insurance',
                                        store={
                                        'res.partner': (lambda self, cr,uid,ids,c: ids, ['plan_ids'], 10),
                                        'tgb.customer.policy.alert':(_get_customer_policy_alert_ids, ['medical_reimbursement'], 10),}),

        'tgb_birthday':fields.date('Birthday'),
        'material_status':fields.selection([('married','Married'),('single','Single'),('divorce','Divorce'),('others','Others')],'Material Status'),
        'dependant':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')],'Dependants '),
        'tgb_birthday_month':fields.function(_get_birthday_detail,type='integer',size=12,string='Birthday month',
                     store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['tgb_birthday'], 10),
            },multi='birthday'),
        'tgb_birthday_day':fields.function(_get_birthday_detail,type='integer',size=12,string='Birthday day',
                     store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['tgb_birthday'], 10),
            },multi='birthday'),

    }
res_partner()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

