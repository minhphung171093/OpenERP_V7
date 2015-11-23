# -*- coding: utf-8 -*-
##############################################################################
#     
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import osv, fields
from tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from dateutil import parser
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import time

class roster_timesheet(osv.Model):
    
    _name = 'roster.timesheet'
    
    _columns = {
        'employee_id':fields.many2one('hr.employee', 'Employee',required=True), 
        'counter_id':fields.many2one('sale.shop', 'Counter'), 
        'current_date':fields.date('Date',select=1,required=True), 
        'time_from':fields.datetime('Time From' ,required=True), 
        'time_to':fields.datetime('Time To',required=True), 
        'state': fields.selection([('open', 'Waiting For Approval'), 
                                    ('draft', 'Draft'), 
                                    ('done', 'Done')], 'State', \
                                    size=16, readonly=True),
        }
    _defaults = {
        'state': 'draft',
        'current_date': lambda *a: time.strftime('%Y-%m-%d'),
        'time_from': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'time_to': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    def _check_date(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            from_date =datetime.strptime(data.time_from[:-9],DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(data.time_to[:-9],DEFAULT_SERVER_DATE_FORMAT)
            first_day =datetime.strftime(from_date,DEFAULT_SERVER_DATE_FORMAT)
            last_day = datetime.strftime(to_date,DEFAULT_SERVER_DATE_FORMAT)
            if (data.current_date != first_day or data.current_date != last_day):
                return False
        return True
    
    _constraints = [
        (_check_date, 'Current Date ,Time From  & Time To  Must have  the Same Date.', ['Warning !!']),
        ]
    
    def case_reset(self, cr, uid, ids, *args):
        """Resets case as draft
        :param ids: List of case Ids
            """
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def case_open(self, cr, uid, ids, *args):
        """Opens Case
        :param ids: List of case Ids
        """
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    def case_close(self, cr, uid, ids, *args):
        """Closes Case
        :param ids: List of case Ids
        """
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def create_employee_timesheets(self, cr, uid, ids=None, context=None):
        """ creats Employee's Timesheet for Previous 
            Month Those are In Done state From Roster Planning. """
            
        timesheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        hr_attendance_obj = self.pool.get('hr.attendance')
        previous_month_obj = parser.parse(time.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
        total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
        first_day_of_previous_month = datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) ,'%d-%m-%Y')
        last_day_of_previous_month = datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) ,'%d-%m-%Y')
        final_first_day_of_pre_month = datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        final_last_day_of_pre_month = datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
        employee_ids = self.search(cr,uid,[('state','=','done'),('current_date','>=',final_first_day_of_pre_month),('current_date','<=',final_last_day_of_pre_month)])
        if employee_ids:
            for employee in self.browse(cr, uid, employee_ids):
                timesheet_ids = timesheet_obj.search(cr, uid, [('date_from','=',final_first_day_of_pre_month),('date_to','=',final_last_day_of_pre_month),('employee_id','=',employee.employee_id.id)])
                if not timesheet_ids:
                    timesheet_obj.create(cr,uid,{'employee_id':employee.employee_id.id,
                                                 'date_from':final_first_day_of_pre_month,
                                                 'date_to':final_last_day_of_pre_month,
                                                 'date_current':employee.current_date,
                                                },context=context)
                hr_attendance_obj.create(cr, uid, {'name':employee.time_from,'action':'sign_in','employee_id':employee.employee_id.id},context=context)
                hr_attendance_obj.create(cr, uid, {'name':employee.time_to,'action':'sign_out','employee_id':employee.employee_id.id},context=context)
        return True


class hr_timesheet_sheet(osv.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    _columns = {
                'state' : fields.selection([
                ('new', 'New'),
                ('draft','Open'),
                ('confirm','Waiting For Pre-Approval'),
                ('final_confirm','Waiting For Final-Approval'),
                ('done','Approved')], 'State', select=True, required=True, readonly=True,
                help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed timesheet. \
                 \n* The \'Confirmed\' state is used for to confirm the timesheet by Manager. \
                 \n* The \'Final Confirmed\' state is used for to confirm the timesheet by Manager. \
                 \n* The \'Done\' state is used when users timesheet is accepted by Timesheet Manager.'),
    }

    _defaults = {
        'state': 'new',
    }

    def do_email(self, cr, uid, timesheet_id, email, subject, message, type, context):
        try:
            obj_mail_server =self.pool.get('ir.mail_server')
            res_user_obj = self.pool.get('res.users')
            user = res_user_obj.browse(cr,uid,uid)
            mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
            mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
            existing_date = timesheet_id.date_from
            from_date =datetime.strptime(existing_date,DEFAULT_SERVER_DATE_FORMAT)
            month  = calendar.month_name[from_date.month]
            name = timesheet_id.employee_id.name
            if(type == 'manager'):
                body = 'Hi,<br/><br/> \
                       The timesheet of <b> %s </b> for the month of <b> %s </b> is ready for <b>%s</b> <br/><br/> \
                       Please login to iServer to %s /Reject. ' % (name,month,message,message)
            if(type == 'user'):
                body =  'Hi, <br/><br/> \
                        The timesheet of <b> %s </b> for the month of <b> %s </b> is now in draft State <br/><br/> \
                        Draft state is set by <b> %s </b> <br/><br/>\
                        Please login to iServer to amend/set to Waiting For Pre-Approval' % (name,month,user.name)
            message_admin  = obj_mail_server.build_email(
                email_from=mail_server_record.smtp_user,
                email_to = [email],
                subject=subject,
                body=body,
                body_alternative = body ,
                email_cc=None,
                email_bcc=None,
                reply_to=mail_server_record.smtp_user,
                attachments=None,
                references = None,
                object_id=None,
                subtype='html', #It can be plain or html
                subtype_alternative=None,
                headers=None)
            obj_mail_server.send_email(cr, uid, message = message_admin, mail_server_id=mail_server_ids[0], context=context)
        except:
            pass
        return True
    
    def mail_to_indirect_manager(self,cr,uid,ids,context=None):
        for timesheet in self.browse(cr,uid,ids,context=context):
            if timesheet.employee_id.parent_id2:
                email = timesheet.employee_id.parent_id2.work_email
                if not email and timesheet.employee_id.parent_id2.user_id and timesheet.employee_id.parent_id2.user_id.user_email:
                    email = timesheet.employee_id.parent_id2.user_id.user_email
                if not email:
                    raise osv.except_osv(_('Mail Error'), _('No email address specified for  Indirect Manager %s !') % (timesheet.employee_id.parent_id2.name))
                self.do_email(cr, uid, timesheet, email, "Waiting For Final-Approval", "Final-Approval", "manager", context)
            else:
                raise osv.except_osv(_('No Manager Error'), _(' %s is not belong to any Indirect Manager!') % (timesheet.employee_id.name))
        return True
    
    def button_confirm(self, cr, uid,ids,context=None):
        """ Override for Sending e-mail to manager 
        that Perticluar Employee has submitted thier timesheet. """
            
        result = super(hr_timesheet_sheet, self).button_confirm(cr, uid,ids,context=context)
        for timesheet in self.browse(cr,uid,ids,context=context):
            if timesheet.employee_id.parent_id:
                email = timesheet.employee_id.parent_id.work_email
                if not email and timesheet.employee_id.parent_id.user_id and timesheet.employee_id.parent_id.user_id.user_email:
                    if timesheet.employee_id.parent_id2:
                        if timesheet.employee_id.parent_id2.user_id.user_email:
                            email = timesheet.employee_id.parent_id2.user_id.user_email
                if not email:
                    print (_('Mail Error'), _('No email address specified for  Indirect Manager %s !') % (timesheet.employee_id.parent_id2.name))
                if email:
                    self.do_email(cr, uid, timesheet, email, "Waiting For Pre-Approval", "Pre-Approval", "manager", context)
            else:
                raise osv.except_osv(_('No Manager Error'), _(' %s is not belong to any Direct Manager!') % (timesheet.employee_id.name))
        return result

    def action_set_to_draft(self, cr, uid, ids, *args):
        """ Override for Sending e-mail to Employee 
        If He/She 's Timesheet will Rejected By Manager. """
        result = super(hr_timesheet_sheet, self).action_set_to_draft(cr, uid, ids, *args)
        context = {}
        context.update(args[0])
        for timesheet in self.browse(cr,uid,ids,context=context):
            if timesheet.employee_id:
                email = timesheet.employee_id.work_email
                if not email and timesheet.employee_id.user_id and timesheet.employee_id.user_id.user_email:
                    email = timesheet.employee_id.user_id.user_email
                if not email:
                    raise osv.except_osv(_('Mail Error'), _('No email address specified for %s !') % (timesheet.employee_id.name))
                self.do_email(cr, uid, timesheet, email, "Timesheet Approval-Rejected","", "user", context)
        return result


class hr_payslip(osv.Model):
    
    _inherit = 'hr.payslip'
     
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id, contract_id, context=None):
        result = super(hr_payslip,self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
        hr_timsheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        emp_timesheet_ids = hr_timsheet_obj.search(cr,uid,[('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','=',employee_id)])
        if emp_timesheet_ids:
            for emp_timesheet_id in hr_timsheet_obj.browse(cr,uid,emp_timesheet_ids):
                days = len(emp_timesheet_id.period_ids)
                total_hours = emp_timesheet_id.total_attendance
                description = "Timesheet From :" + date_from + " To :"+date_to
                code ="TIMESHEETDAYS"
                result.get('value').get('worked_days_line_ids',[]).append({'number_of_days':days,'number_of_hours':total_hours,'name':description,'code':code})
        return result

