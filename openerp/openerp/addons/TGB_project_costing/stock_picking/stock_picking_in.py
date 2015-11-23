
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_picking_in(osv.osv):
    _name='stock.picking.in'
    _inherit='stock.picking.in'
            
    _columns = {
        'shipment_no':fields.char('Shipment No',size=20,required=True),
        'source_voucher_no':fields.char('Source Voucher No.',size=20,),
        'supplier_id':fields.many2one('res.partner','Supplier',domain=[('customer','=',False)],required=True),
        'supplier_do_no':fields.char('Supplier DO No.',size=20,),
        'supplier_do_date':fields.date('Supplier DO Date',required=True),
        'supplier_invoice_no':fields.char('Supplier Invoice No.',size=20,),
        'supplier_invoice_date':fields.date('Supplier Invoice Date',required=True),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),),
        'currency_id':fields.many2one('res.currency',string='Currency',),
        'grn_no':fields.char('GRN No.',size=20,),
        'source_shipment_no':fields.char('Source Shipment No.',size=20,),
        'actual_shipment_date':fields.date('Actual Shipment Date',),
        'estimated_shipment_date':fields.date('Estimated Shipment Date',required=True),
        'actual_arrival_date':fields.date('Actual Arrival Date',),
        'estimated_arrival_date':fields.date('Estimated Arrival Date',required=True),
        'goods_receipt_date':fields.date('Goods Receipt Date',),
        'reference_no':fields.char('Reference No.',size=20,),
        'shipment_mode_term':fields.char('Shipment Mode / Term',size=20,),
        'receiving_location':fields.many2one('stock.location',string='Receiving Location',),
        'forwarder_id':fields.many2one('construction.party',string='Forwarder',),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks':fields.text('External Remarks',),
        'allocation_detail_ids':fields.one2many('stock.picking.allocation.detail','stock_picking_in_id',string='Allocation Details',),
        'additional_cost':fields.one2many('stock.picking.additional.cost','stock_picking_in_id',string='Additional Cost',),
        'booking_date':fields.date('Booking Date',),
        'port_of_load':fields.many2one('res.country.port',string='Port Of Load',),
        'port_of_fd':fields.many2one('res.country.port',string='Port Of FD',),
        'port_of_dischg':fields.many2one('res.country.port',string='Port Of Dischg',),
        'country_id':fields.many2one('res.country',string='Country',),
        'carrier_id':fields.many2one('stock.picking.carrier',string='Carrier',),
        'eta_etd_pol':fields.date('ETA/ETD (POL)',),
        'eta_fd':fields.date('ETA (FD)',),
        'date_of_manufacture':fields.date('Date of Manufacture',),
        'eta_time_pol':fields.char('ETA - Time (POL) hh:mm',size=5,),
        'eta_time_fd':fields.char('ETA - Time (FD) hh:mm',size=5,),
        'products_description':fields.char('Products Description',size=100,),
        'remarks_trucker_haulier':fields.text('Remarks to Trucker / Haulier',),
        'shipping_marks':fields.text('Shipping Marks',),
        'priority':fields.selection([('high','High'),('normal','Normal'),('low','Low'),],'Priority',),
        'attachment_ids':fields.one2many('project.attachment','stock_picking_in_id',string='Attachments',),
        'contact_id':fields.many2one('res.partner',string='Contact Person',),
        }
    
    _defaults={
        'supplier_do_date':fields.date.context_today,
        'estimated_shipment_date':fields.date.context_today,
        'supplier_invoice_date':fields.date.context_today,
        'estimated_shipment_date':fields.date.context_today,
        'estimated_arrival_date':fields.date.context_today,
    }

stock_picking_in()
