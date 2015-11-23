from osv import osv,fields
import time

class inactive_status(osv.osv_memory):
    _name='inactive.status'
    
    _columns = {
        'inact_date' : fields.datetime('Inactive Date'),
        'reason':fields.text('Reason')
    }
    
    _defaults = {
        'inact_date' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    def submit(self,cr,uid,ids,context=None):
        wiz_recs = self.browse(cr, uid, ids,context=context)
        emp_obj = self.pool.get('hr.employee')
        
        for wiz_rec in wiz_recs:
            vals = {
                'inact_date':wiz_rec.inact_date,
                'reason' :wiz_rec.reason,
            }
            emp_obj.write(cr, uid, context['active_id'],vals, context=context)
        return True
    
    def cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
inactive_status()