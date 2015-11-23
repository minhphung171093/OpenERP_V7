# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from tools.translate import _

class monthly_attendance_sheet(osv.TransientModel):
    """
    For Monthly Attendance Sheet
    """
    _name = "monthly.attendance.sheet"
    _description = "Monthly Attendance Sheet Wizard"
    _columns = {
        'standard_id': fields.many2one('school.standard', 'Academic Class', required=True ),
        'year_id': fields.many2one('academic.year', 'Year', required=True),
        'month_id': fields.many2one('academic.month', 'Month', required=True)
    }
    
    def monthly_attendance_sheet_open_window(self, cr, uid, ids, context=None):
        ''' This method open new window with monthly attendance sheet
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : record of monthly attendance sheet        
        '''
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        data = self.read(cr, uid, ids, [], context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'school_attendance', 'action_attendance_sheet_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)
        
        result = result and result[0]
        domain = [('standard_id', 'in', [data['standard_id'][0]]), ('month_id', 'in',[data['month_id'][0]]), ('year_id', 'in',[data['year_id'][0]])]
        res_ids = self.pool.get('attendance.sheet').search(cr, uid, domain, context=context)
        result['res_id'] = res_ids and res_ids[0] or False
        
        if result['res_id']==False:
            raise osv.except_osv(_('Record Not Found!'),_('No Entry Done in The Daily Attendence..!!'))
        return result

monthly_attendance_sheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
