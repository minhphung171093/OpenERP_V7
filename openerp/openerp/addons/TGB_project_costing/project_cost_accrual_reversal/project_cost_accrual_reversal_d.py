
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_cost_accrual_reversal_detail(osv.osv):
    _name='project.cost.accrual.reversal.detail'
    def _home_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for detail in self.browse(cr,uid,ids):
            if detail.project_cost_accrual_reversal_id:
                res[detail.id] = detail.accrual_amount*detail.project_cost_accrual_reversal_id.exchange_rate
        return res
    _columns = {

        'product_id':fields.many2one('product.product',string='Item',required=True),
        'product_description':fields.related('product_id','description',string='Description',type='char'),
        'product_uom_id':fields.related('product_id','uom_id',type='many2one',relation='product.uom',string='UOM',readonly=True),
        'accrual_amount':fields.float('Accrual Amt',digits_compute=dp.get_precision('Account'),),
        'accrual_home_amount': fields.function(_home_amount, string='Accrual Home Amt', type='float',
                                            digits_compute=dp.get_precision('Account')),
        'project_cost_accrual_reversal_id':fields.many2one('project.cost.accural.resersal',string='Project Cost Accrual Reversal',),
        'project_cost_accrual_allocation_detail_ids':fields.one2many('project.cost.accrual.allocation.detail','project_cost_accrual_reversal_detail_id',string = 'Project Allocation Detail')
        }
    
    _defaults={
    }
project_cost_accrual_reversal_detail()

class project_cost_accrual_allocation_detail(osv.osv):
    _name = 'project.cost.accrual.allocation.detail'

    def _home_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for detail in self.browse(cr,uid,ids):
            if detail.project_cost_accrual_reversal_detail_id.project_cost_accrual_reversal_id:
                res[detail.id] = detail.alloc_accrual_amt*detail.project_cost_accrual_reversal_detail_id.project_cost_accrual_reversal_id.exchange_rate
        return res

    _columns = {
        'project_cost_accrual_reversal_detail_id':fields.many2one('project.cost.accrual.reversal.detail', 'detail id'),
        'product_id':fields.many2one('product.product','Phase Seq No'),
        'line_item_seq_no':fields.float('Line Item Seq No',digits_compute=dp.get_precision('Account'),),
        'alloc_accrual_amt':fields.float('Alloc Accrual Amt',digits_compute=dp.get_precision('Account'),),
        'alloc_accrual_home_amt':fields.function(_home_amount, string='Accrual Home Amt', type='float',
                                            digits_compute=dp.get_precision('Account')),

    }


