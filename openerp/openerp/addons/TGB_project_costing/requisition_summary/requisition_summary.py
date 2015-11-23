
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class requisition_summary(osv.osv):
    _name='requisition.summary'
    _columns = {
        'purchase_requisition_no':fields.char('Purchase Requisition No',size=20,),
        'copy_from':fields.char('Copy From',size=100,readonly=True),
        'copy':fields.many2one('requisition.summary',string='Copy',),
        'requestor':fields.many2one('res.partner',string='Requestor',required=True),
        'purchase_requisition_date':fields.date('Purchase Requisition Date',required=True),
        'reference_no':fields.char('Reference No.',size=20,),
        'subject_header':fields.char('Subject',size=100,),
        'shipment_mode':fields.many2one('project.shipment.mode',string='Shipment Mode',required=True),
        'shipment_term':fields.many2one('project.shipment.term',string='Shipment Term',required=True),
        'port_of_loading':fields.many2one('res.country.port',string='Port of Loading',),
        'country_of_loading':fields.many2one('res.country',string='Country of Loading',),
        'port_of_discharge':fields.many2one('res.country.port',string='Port of Discharge',),
        'country_of_discharge':fields.many2one('res.country',string='Country of Discharge',),
        'port_final_destination':fields.many2one('res.country.port',string='Port of Final Destination',),
        'country_final_destination':fields.many2one('res.country',string='Country of Final Destination',),
        'ship_through':fields.many2one('construction.party',string='Ship Through',),
        'default_to_location':fields.many2one('stock.location',string='Default ship to Location',required=True),
        'no_of_shipment':fields.integer('No. of Shipment',),
        'origin_voucher_no':fields.char('Origin Voucher No',size=20,required=True),
        'customer_id':fields.many2one('res.partner',string='Customer',),
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'customer_item_no':fields.char('Customer PO Line Item No',size=20,),
        'customer_so_no':fields.char('Customer SO No',size=20,),
        'subject_detail':fields.char('Subject',size=100,),
        'source_pp_no':fields.char('Source PP No',size=20,),
        'pp_partial_no':fields.char('PP Partial No',size=20,),
        'finished_good':fields.many2one('product.product',string='Finished Good',),
        'own_inventory':fields.many2one('stock.warehouse',string='Own Inventory',),
        'production_due_date':fields.date('Production Due Date',),
        'required_shipment_date':fields.date('Required Shipment Date',),
        'internal_remarks_code':fields.many2one('project.remark',string='Internal Remarks Code',),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks_code':fields.many2one('project.remark',string='External Remarks Code',),
        'external_remarks':fields.text('External Remarks',),
        'requisition_summary_detail_ids':fields.one2many('requisition.summary.detail','requisition_summary_id',string='Detail',),
        'allocation_detail_ids':fields.one2many('stock.picking.allocation.detail','requisition_summary_id',string='Allocation Details',),
        'status':fields.char('Status',size=5),
        }
    
    _defaults={
        'copy_from':'PR Draft/Pending Draft/Cost Confirmation/Pending Approval/History',
        'purchase_requisition_date':fields.date.context_today,
        'no_of_shipment':1,
        'required_shipment_date':fields.date.context_today,
    }

requisition_summary()
