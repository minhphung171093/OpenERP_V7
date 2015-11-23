
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_cost_accrual_reversal(osv.osv):
    _name='project.cost.accural.resersal'
    _columns = {
        'cost_accrual_voucher':fields.char('Cost Accrual Voucher',size=20,),
        'cost_accrual_date':fields.date('Cost Accrual Date', required=True),
        'project no':fields.many2one('project.project',string='Project No',required=True),
        'customer':fields.many2one('res.partner',string='Customer',),
        'currency':fields.many2one('res.currency',string='Currency',required=True),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),required=True),
        'reference no':fields.char('Reference No',size=20,),
        'internal_remarks_code':fields.many2one('project.remark',string='Internal Remarks Code',domain=[('type','=','internal')]),
        'internal remarks':fields.text('Internal Remarks',),
        'external_remarks_code':fields.many2one('project.remark',string='External Remarks Code',domain=[('type','=','external')]),
        'external remarks':fields.text('External Remarks',),
        'project_cost_accrual_reversal_detail_ids':fields.one2many('project.cost.accrual.reversal.detail','project_cost_accrual_reversal_id',string='Detail',),
        }
    
    _defaults={
        'cost_accrual_date': fields.date.context_today,
        'exchange_rate':1,
    }

project_cost_accrual_reversal()
