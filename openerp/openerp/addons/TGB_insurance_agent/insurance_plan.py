# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class TGB_insurance_plan(osv.osv):
    _name = 'tgb.insurance.plan'
    _columns = {
        'name': fields.char('Plan name', size=50, select=1),
        'code':fields.char('Code',size=5,),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(TGB_insurance_plan,self).default_get(cr,uid,fields,context)
        res['code'] = self.pool.get('ir.sequence').get(cr, uid, 'tgb.code.insurance.plan')
        return res
TGB_insurance_plan()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

