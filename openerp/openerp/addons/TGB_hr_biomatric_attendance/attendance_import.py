# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import psycopg2
from openerp.osv import orm, fields
import xlrd
from base64 import b64decode
from openerp.tools.translate import _
from datetime import datetime, date, timedelta
import math


class attendance_import(orm.TransientModel):
    _inherit = 'base_import.import'
    _name = 'attendance.import'


    def do(self, cr, uid, ids,context=None):
        def float_time_convert(float_val):
            factor = float_val < 0 and -1 or 1
            val = abs(float_val)
            return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

        cr.execute('SAVEPOINT import')
        record = self.browse(cr, uid, ids, context=context)[0]
        workbook = xlrd.open_workbook(file_contents=b64decode(record.file))
        sheet = workbook.sheet_by_index(0)
        for r in range(0,sheet.nrows):
            if r>=4:
                row = sheet.row_values(r)
                user_name = row[1]
                user_ids = self.pool.get('res.users').search(cr,uid,[('login','=',user_name.lower())])
                if not user_ids or len(user_ids)==0:
                    raise osv.except_osv(_('Error!'),_("No user name %s ") % (user_name))
                else:
                    user_id = user_ids[0]
                    employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',user_id)])
                    if not employee_id or len(employee_id)==0:
                        raise osv.except_osv(_('Error!'),_("No employee defined %s ") % (user_name))
                    employee_id = employee_id[0]
                    start_date = record.period_id.date_start
                    stop_date = record.period_id.date_stop
                    current_date =  datetime.strptime(start_date, '%Y-%m-%d')
                    end_date =  datetime.strptime(stop_date, '%Y-%m-%d')
                    for i in range(3,len(row)):
                        if current_date<=end_date:
                            shift = row[i]
                            if shift and shift>0:
                                shift_id = self.pool.get('hr.time.table').search(cr,uid,[('shift_no','=',shift)])
                                if not shift_id or len(shift_id)==0:
                                    raise osv.except_osv(_('Error!'),_("No Shift defined for %s ") % (shift))
                                shift_id=shift_id[0]
                                timesheet_id = self.pool.get('hr_timesheet_sheet.sheet').search(cr,uid,[('employee_id','=',employee_id),('date_from','<=',current_date),('date_to','>=',current_date)])
                                if not timesheet_id or len(timesheet_id)==0:
                                    raise osv.except_osv(_('Error!'),_("No timesheet for %s at %s ") % (user_name, current_date))
                                timesheet_id=timesheet_id[0]
                                print 'sheet ',timesheet_id
                                shift_obj = self.pool.get('hr.time.table').browse(cr,uid,shift_id)
                                attendance_obj = self.pool.get('hr.attendance')

                                if shift_obj.am_in:
                                    am_in = shift_obj.am_in
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time , timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_in','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create am in'

                                if shift_obj.am_out:
                                    am_in = shift_obj.am_out
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time, timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_out','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create am out'

                                if shift_obj.pm_in:
                                    am_in = shift_obj.pm_in
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time, timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_in','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create pm in'


                                if shift_obj.pm_out:
                                    am_in = shift_obj.pm_out
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time, timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_out','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create pm out'

                                if shift_obj.ot_in:
                                    am_in = shift_obj.ot_in
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time, timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_in','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create ot in'

                                if shift_obj.ot_out:
                                    am_in = shift_obj.ot_out
                                    in_hour, in_min = float_time_convert(am_in)
                                    in_time= current_date + timedelta(hours=in_hour,minutes=in_min)
                                    print 'in time', in_time, timesheet_id
                                    attendance_obj.create(cr,uid,{'action':'sign_out','name':in_time.strftime('%Y-%m-%d %H:%M:%S'),'employee_id':employee_id})
                                    print 'create ot out'

                            current_date +=timedelta(days=1)


        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return True





    _columns = {
        'period_id':fields.many2one('account.period','Period',required=True),

    }

