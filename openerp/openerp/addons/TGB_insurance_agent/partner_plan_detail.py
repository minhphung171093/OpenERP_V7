# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class TGB_partner_plan_detail(osv.osv):
    _name = 'tgb.partner.plan.detail'
    _columns = {
        'plan_id': fields.many2one('tgb.insurance.plan','Insurance Plan',required=True),
        'partner_id':fields.many2one('res.partner','Customer'),
        'date_of_alert':fields.date('Day of Alert'),
        'remark':fields.char('Remark',size=100),
        'death_benefit':fields.float('Death Benefit',digits=(16,2)),
        'total_permanent_disability':fields.float('Total & Permanent Disability ',digits=(16,2)),
        'critical_illness':fields.float('Critical illness ',digits=(16,2)),
        'accident_cover':fields.float('Accident Cover',digits=(16,2)),
        'inception_date':fields.date('Inception Date'),
        'maturity_date':fields.date('Maturity Date'),
        'maturity_value':fields.float('Maturity Value',digits=(16,2)),
        'year_inforce':fields.integer('Year Inforce',size=5),
        'yearly_premium':fields.float('Yearly Premium',digits=(16,2)),
        'monthly_premium':fields.float('Monthly Premium',digits=(16,2)),
        'early_crisis':fields.float('Early Crisis',digits=(16,2)),
        'medical_reimbursement':fields.float('Medical Reimbursement',digits=(16,2)),
        'remark2':fields.char('Remark',size=100),
    }
TGB_partner_plan_detail()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

