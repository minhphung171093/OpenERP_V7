# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from openerp import tools
import re


class cpf_submission(osv.osv_memory):
    _name = 'cpf.submission'
    _description = 'CPF submission'
    
    global month 
    month = [(1, 'Janyary'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'),
              (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'),(12, 'December'),]
    
    _columns = {
        #'month': fields.selection(month, 'Month', required=True),
        'file_date': fields.date('Date',required=True),
        'company_id': fields.many2one('res.company','Company',required=True),
        'employee_ids': fields.many2many('hr.employee','cpf_employee_submission_rel', 'emp_id', 'cpf_id', 'Employee'),
    }

    def action_apply(self, cr, uid, ids, context=None):
        res_company = self.pool.get('res.company')
        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        mod_obj = self.pool.get('ir.model.data')
        ir_obj = self.pool.get('ir.attachment')
        cpf_obj = self.pool.get('cpf.submission.file')
        wizard = self.browse(cr, uid, ids[0], context)
        company = res_company.browse(cr, uid, wizard.company_id.id, context)
        file_month = datetime.strptime(wizard.file_date , '%Y-%m-%d')
        file_name = str(company.cpf_number)+str(month[file_month.month-1][1][:3])+str(datetime.now().year)+'01.dtl'
        count , wage= 0, 0
        emp_list = []
        file_data =''
        file_data = 'F%s%sPTE01%s01%s%s%s%s%s%s%s%s\n' % ( ' '.ljust(1,' '),str(wizard.company_id.passport_id).rjust(10,'0'),' '.ljust(1,' '),str(datetime.now().year).rjust(4,'0'), str(datetime.now().month).rjust(2,'0'),str(datetime.now().day).rjust(2,'0'),str(datetime.now().hour).rjust(2,'0'),str(datetime.now().minute).rjust(2,'0'),str(datetime.now().second).rjust(2,'0'),'FTP.DTL'.ljust(13,' '),' '.rjust(103,' ')) 
        employee_id = [employee.id for employee in wizard.employee_ids]
        for emp in employee_obj.browse(cr, uid, employee_id, context):
            emp_payslip = payslip_obj.search(cr, uid, [('employee_id', '=', emp.id), ('date_from', '<=' , file_month.date()),('date_to', '>=', file_month.date()), ('state', '=', 'done')], context=context)
            if not emp_payslip:
                raise osv.except_osv(_('Warning!'),_(" %s employee which payslip is not genreate for this period !") % (emp.name,))
            emp_list.append(emp.id)
            count +=1
            file_data += 'F0%sPTE01%s01%s%s01%s%s%s\n' % (str(wizard.company_id.passport_id).rjust(10,'0'),' '.rjust(1,' '),str(datetime.now().year).rjust(4,'0'), str(datetime.now().month).rjust(2,'0'),str('0').rjust(12,'0'),str('0').rjust(7,'0'),' '.rjust(103,' '))
        for emp in employee_obj.browse(cr, uid, employee_id, context):
            if emp.contract_id:
                wage = emp.contract_id.wage
            count +=1
            file_data += 'F1%sPTE01%s01%s%s01%s%s%s%s%s%s%s\n' % (str(wizard.company_id.passport_id).rjust(10,'0'),' '.rjust(1,' '),str(datetime.now().year).rjust(4,'0'), str(datetime.now().month).rjust(2,'0'),str(emp.bank_account_id.acc_number).rjust(9,'0'),str(int(wage)).rjust(12,'0'),str('0').rjust(10,'0'),str('0').rjust(10,'0'),'E',str(emp.name).ljust(22,' '),' '.rjust(58,' ')) 
        file_data += 'F9%sPTE01%s01%s%s%s\n' % (str(wizard.company_id.passport_id).rjust(10,'0'),' '.rjust(1,' '),str(count+2).ljust(7,'0'),str('0').rjust(15,'0'),' '.rjust(108,' '))
        cpf_id = cpf_obj.create(cr, uid, {'name': file_name,'state': 'draft','employee_ids': [(6,0, emp_list)],'user_id': uid, 'date': datetime.now()},context=context)
        vals = {
            'name': file_name,
            'res_model': 'cpf.submission.file',
            'res_id': cpf_id or False,
            'datas': file_data.encode('base64')
        }
        file_id = ir_obj.create(cr, uid, vals,context=context)
        cpf_obj.write(cr, uid, cpf_id, {'cpf_file_id': file_id}, context=context)
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'view_cpf_submission_file_form')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {'name': _('CPF Submission File'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cpf.submission.file',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'res_id': cpf_id or False,
        }