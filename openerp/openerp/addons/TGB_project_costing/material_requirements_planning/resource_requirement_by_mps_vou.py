
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class resource_requirement_by_mps_vou(osv.osv):
    _name='resource.requirement.by.mps.vou'
    _columns = {
        'mps_voucher_no':fields.char('MPS Voucher No',size=20,),
        'source_voucher_no':fields.char('Source Voucher No',size=20,),
        'source_sequence_no':fields.char('Source Phase Sequence No',size=20,),
        'source_schedule_no':fields.char('Source Schedule No',size=20,),
        'pp_voucher_no':fields.char('PP Voucher No',size=20,),
        'customer_omer_customer':fields.many2one('res.partner',string='Customer',),
        'finished_goods_code':fields.char('Finished Goods Code',size=20,),
        'required_procurement_date':fields.date('Required Procurement Date',),
        'production_due_date':fields.date('Production Due Date',),
        'required_shipment_date':fields.date('Required Shipment Date',),
        'qty_qty_required':fields.float('Qty Required',digits_compute=dp.get_precision('Account'),),
        'qoh_qoh_allocated':fields.float('QoH Allocated',digits_compute=dp.get_precision('Account'),),
        'qoor_qoor_allocated':fields.float('QoOR Allocated',digits_compute=dp.get_precision('Account'),),
        'ost_qty_allocated':fields.float('Ost PR Qty Allocated',digits_compute=dp.get_precision('Account'),),
        'draft_qty_allocated':fields.float('Draft PR Qty Allocated',digits_compute=dp.get_precision('Account'),),
        'pr_to_raise':fields.float('PR Qty to Raise',digits_compute=dp.get_precision('Account'),),
        'sel_no':fields.float('Sel No',digits_compute=dp.get_precision('Account'),),
        'requirement_planning_id':fields.many2one('material.requirements.planning',string='Plan',),
        }
    
    _defaults={
    }

resource_requirement_by_mps_vou()
