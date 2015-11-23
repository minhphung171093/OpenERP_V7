
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_scheduler(osv.osv):
    _name='project.scheduler'
    _columns = {
        'project_no':fields.many2one('project.project',string='Project No',),
        'revision_no':fields.char('Revision No',size=5,),
        'customer':fields.related('customer_name','ref',string='Customer',type='char',readonly=True),
        'customer_name':fields.many2one('res.partner',string='Customer Name',),
        'customer_no':fields.char('Customer Job No.',size=20,),
        'customer_revision_no':fields.char('Customer Revision No',size=5,),
        'bill_type':fields.selection([('bill_by_project','Bill By Project'),('bill_by_phase','Bill By Phase'),],'Bill Type',),
        'prompt_po_value':fields.selection([('yes','Yes'),('no','No'),],'Prompt If Bill Exceed Customer PO Value',),
        'estimate_date':fields.date('Estimate Date',),
        'customer_contact':fields.many2one('project.customer.contract',string='Customer Contact',),
        'start_date':fields.date('Start Date',),
        'end_date':fields.date('End Date',),
        'project_class':fields.many2one('project.class',string='Project Class',),
        'project_category':fields.many2one('project.category',string='Project Category',),
        'currency':fields.many2one('res.currency',string='Currency',),
        'sales_tax':fields.many2one('account.tax',string='Sales Tax',),
        'retention_required':fields.float('Retention Required',digits_compute=dp.get_precision('Account'),),
        'max_retention_amt':fields.float('Max Retention Amt',digits_compute=dp.get_precision('Account'),),
        'sales_person':fields.many2one('res.users',string='Sales Person',),
        'sales_manager':fields.many2one('res.users',string='Sales Manager',),
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'reference_no':fields.char('Reference No',size=20,),
        'default_loading_location':fields.many2one('stock.location',string='Default Loading Location',),
        'commission_group':fields.many2one('project.commision.group',string='Commission Group',),
        'ship_to_address':fields.char('Ship To Address',size=100,),
        'ship_to_contact':fields.many2one('res.partner',string='Ship To Contact',),
        'requested_shipment_date':fields.date('Requested Shipment Date',),
        'default_shm_priority':fields.char('Default Shm Priority',size=100,),
        'subject':fields.char('Subject',size=100,),
        'project_scheduler_inventory_ids':fields.one2many('project.scheduler.inventory','project_scheduler_id',string='Inventory',),
        'project_scheduler_service_ids':fields.one2many('project.scheduler.service','project_scheduler_id',string='Services',),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks':fields.text('External Remarks',),
        }
    
    _defaults={
    }

project_scheduler()
