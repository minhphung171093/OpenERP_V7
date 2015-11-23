# -*- coding: utf-8 -*-

from osv import osv, fields
import netsvc

class refuse_leave(osv.osv_memory):
    _name = 'refuse.leave'
    
    _columns ={
        'reason' : fields.text ('Reason'), 
    }
    def add_reason(self, cr, uid, ids, context=None):
        hr_holidays_obj = self.pool.get('hr.holidays')
        if not context.get('active_id'):
            return {}
        user_data = self.pool.get('res.users').browse(cr, uid, uid, context)
        wf_service = netsvc.LocalService('workflow')
        hr_holidays_data = hr_holidays_obj.browse(cr, uid, context.get('active_id'))
        for data in self.browse(cr, uid, ids, context):
            if data.reason:
                new_data = ''
                if context.get('cancel'):
                    new_data = "Leave Cancelled Reason. (%s) \n--------------------------------------------------------------------------" % user_data.name
                elif context.get('refuse'):
                    new_data = "Leave Refused Reason. (%s) \n----------------------------------------------------------------------------"  % user_data.name
                orignal_note = ''
                if hr_holidays_data.notes:
                    orignal_note = hr_holidays_data.notes
                reason = orignal_note + "\n\n" + new_data + "\n\n" + data.reason or ''
                hr_holidays_obj.write(cr, uid, [context.get('active_id')], {'notes': reason, 'rejection' : data.reason})
        if context.get('cancel'):
            wf_service.trg_validate(uid, 'hr.holidays', context.get('active_id'), 'cancel', cr)
        if context.get('refuse'):
            wf_service.trg_validate(uid, 'hr.holidays', context.get('active_id'), 'refuse', cr)
        return {'type' : 'ir.actions.act_window_close'}
        
refuse_leave()