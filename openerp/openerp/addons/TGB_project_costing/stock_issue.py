# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_issue(osv.osv):
    _name = 'stock.issue'
    _columns = {
        'issue_type':fields.selection([('cal','Calibration'), ('cmg','Commission Group'), ('cmg','Commission Group'), ('mr','Manufacturing'), ('emp','Employee'), ('phg','Phase Group'), ('prod','Production'), ('proj','Project'), ('scon','Subcon Contract')], 'Issue Type',),
        'si_voucher_no':fields.char('SI Voucher No.',size=20),
        'si_source_voucher_no':fields.char('Source Voucher No.',size=20),
        'si_source_pp_voucher_no':fields.char('Source PP Voucher No.',sizez=20),
        'si_source_partial_pp_no':fields.char('Source Partial PP No.',size=20),
        'work_center_and_machine':fields.char('Work Center and Machine',size=20),
        'manu_res_user_id':fields.many2one('res.users','Issue To'),
        'finished_good':fields.char('Finished Good',size=20),
        'si_date':fields.date('Issue Date'),
        'schedule_start_date':fields.datetime('Scheduled Start Date & Time'),
        'schedule_start_end':fields.datetime('Scheduled End Date & Time'),
        'customer_id':fields.many2one('res.partner','Customer'),
        'stock_location':fields.many2one('stock.warehouse','Stock Location'),
        'res_user_id':fields.many2one('res.users','Issue By'),
        'reference_no':fields.char('Reference No.',size=20),
        'stock_issue_emp_line':fields.one2many('stock.issue.employee','stock_issue_id','Stock Issue Employee'),
        'require_stock_return':fields.selection([('yes','Yes'), ('no','No')], 'Require Stock Return',),

    }
    _default = {
    }

stock_issue()

class stock_issue_employee(osv.osv):
    _name = 'stock.issue.employee'
    def _get_sub_code(self,cr,uid,context={}):
        print 'active ids ', context
        return [('a','nothing')]
    def _get_sub_description(self,cr,uid,ids,a,b,context={}):
        detail = {}
        for emp in self.browse(cr,uid,ids):
            detail[emp.id]='Nothing'
        return detail

    _columns = {
        'stock_issue_id':fields.many2one('stock.issue','Stock Issue'),
        'subject_type':fields.selection([('emp','EMP'), ('grp','GRP')], 'Subject Type',),
        'sub_code':fields.selection(_get_sub_code, 'Subject Code', required=True,
            ),
        'sub_des':fields.function(_get_sub_description, string ='Subject Description',type='char',size=50,
            ),
        'product_id':fields.many2one('product.product','Inventory Code'),
        'product_code':fields.related('product_id','default_code',type='char',string='Inventory Description',store=True,),
        'qty_on_hand':fields.float('Quantity On Hand',digits_compute=dp.get_precision('Account')),
        'qty_available':fields.float('Quantity Available',digits_compute=dp.get_precision('Account')),
        'issue_qty':fields.float('Issue Quantity',digits_compute=dp.get_precision('Account')),
        'pack_size':fields.selection([('loose','LOOSE'),('p6','P6 (6.0)')], 'Pack Size',change_default=True),
        'no_of_pack':fields.float('No. of Pack',digits_compute=dp.get_precision('Account')),
        'serial_no':fields.char('Serial No.',size=20),
    }

    _default = {
    }

stock_issue_employee()



class stock_issue_employee(osv.osv):
    _name = 'stock.issue.manufacturing'

    _columns = {
    }

    _default = {
    }

stock_issue_employee()



