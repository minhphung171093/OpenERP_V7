# -*- coding: utf-8 -*-
from osv import osv, fields
import netsvc

class comput_confirm_payslip_wiz(osv.osv_memory):

    _name = 'comput.confirm.payslip.wiz'

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(comput_confirm_payslip_wiz, self).default_get(cr, uid, fields_list, context)
        res['emp_net_amt_info'] = False
        payslip_obj = self.pool.get('hr.payslip')
        payslip_ids = context.get('active_ids')
        user_obj = self.pool.get('res.users')
        lang_obj = self.pool.get('res.lang')
        user_data = user_obj.browse(cr, uid, uid)
        lang_ids = lang_obj.search(cr, uid, [('code', '=', user_data.context_lang)])
        net_amount = 0.0
        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_amount += line.amount
        if lang_ids:
            net_amount = lang_obj.format(cr, uid, lang_ids, "%.2f", net_amount, True)
        foramte_string = "Total Amount Before Compute is %s" % net_amount
        for payslip in payslip_ids:
            payslip_obj.compute_sheet(cr, uid, [payslip], context=context)
        net_amount = 0.0
        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_amount += line.amount
        if lang_ids:
            net_amount = lang_obj.format(cr, uid, lang_ids, "%.2f", net_amount, True)
        foramte_string += "\nTotal Amount After Compute is %s" % net_amount
        res['name'] = foramte_string
        return res

    def confirm_selected_payslip(self, cr, uid, ids, context):
        if context is None:
            context = {}
        if not context.get('active_ids'):
            return {}
        payslip_obj = self.pool.get('hr.payslip')
        wf_service = netsvc.LocalService("workflow")
        for payslip in context.get('active_ids', []):
            payslip_obj.compute_sheet(cr, uid, [payslip], context=context)
            wf_service.trg_validate(uid, 'hr.payslip', payslip, 'hr_verify_sheet', cr)
        return {}

    _columns = {
        'name': fields.text('Employee Net Amount Information', readonly=True),
    }

comput_confirm_payslip_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: