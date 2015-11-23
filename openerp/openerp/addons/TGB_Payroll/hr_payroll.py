# -*- coding: utf-8 -*-


from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _


class hr_payslip(osv.osv):
    _inherit = "hr.payslip"
    _columns = {
        'tgb_hr_payroll_detail_ids':fields.one2many('tgb.hr.payslip.detail','payslip_id','Daily detail',readonly=True),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        result = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        for payslip in self.browse(cr,uid,ids):
            date_from = payslip.date_from
            date_to = payslip.date_to
            employee_id = payslip.employee_id.id
            contract_id = payslip.contract_id.id
            hr_timsheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
            emp_timesheet_ids = hr_timsheet_obj.search(cr,uid,[('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','=',employee_id),('state','=','done')])
            old_payslip_detail_ids = self.pool.get('tgb.hr.payslip.detail').search(cr,uid,[('payslip_id','=',payslip.id)])
            if old_payslip_detail_ids:
                self.pool.get('tgb.hr.payslip.detail').unlink(cr,uid,old_payslip_detail_ids)
            if emp_timesheet_ids and len(emp_timesheet_ids)>0:
                for emp_timesheet_id in hr_timsheet_obj.browse(cr,uid,emp_timesheet_ids):
                    for timesheet in emp_timesheet_id.timesheet_ids:

                        self.pool.get('tgb.hr.payslip.detail').create(cr,uid,{'payslip_id':payslip.id,
                                                                              'timesheet_detail_id':timesheet.id})
        return result

hr_payslip()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
