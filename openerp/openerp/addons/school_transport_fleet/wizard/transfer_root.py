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

from tools.translate import _
from openerp.osv import fields, osv

class transfer_root(osv.TransientModel): 
    _name = "transfer.root"
    _description = "transfer Point"
    _columns = {
        'name':fields.many2one('student.student', 'Student Name', readonly=True),
        'vehicle_id':fields.many2one('account.asset.asset', 'Vehicle No', readonly=True),
        'participation_id':fields.many2one('transport.participant', 'Participation', required=True),
        'root_id':fields.many2one('student.transport', 'Root', readonly=True),
        'old_point_id' : fields.many2one('transport.point', 'Old Point'),
        'new_point_id' : fields.many2one('transport.point', 'New Point', required=True),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        ''' This method Returns default values for the fields in fields_list.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param fields : list of fields to get the default values for (example [‘field1’, ‘field2’,])
        @param context : standard Dictionary
        @return : dictionary of the default values
        '''
        if context is None:
            context = {}
        result = super(transfer_root, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            student = self.pool.get('student.student').browse(cr, uid, context.get('active_id'), context=context)
            if 'name' in fields:
                result.update({'name': student.id})
        return result
    
    def onchange_participation_id(self, cr, uid, ids, transport, context=None):
        '''This method automatically change value of Participation 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param transport : change value base on this field
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of new point 
        '''
        if transport:
            transport_obj = self.pool.get('transport.participant').browse(cr, uid, transport, context)
            res={}
            root = transport_obj.transport_id.id
            lst=[]
            root_obj = self.pool.get('student.transport').browse(cr , uid,root, context)
            for i in root_obj.trans_point_ids:
                lst.append(i.id)
            domain = "[('id','in',"+str(lst)+")]"
            res={'root_id': transport_obj.transport_id.id, 'vehicle_id': transport_obj.asset_id.id, 'old_point_id':transport_obj.point_id.id}
        return {'value': res,'domain' : {'new_point_id' : domain}}

    def onchange_old(self, cr, uid, ids, transport, context=None):
        '''This method automatically change value of point of transportation 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param transport : change value base on this field
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of point
        '''
        transport_obj = self.pool.get('transport.participant').browse(cr, uid, transport, context)            
        warning = {'title': _('Warning!'),
                    'message': _('You Can Not Change on Old Point')
            }
        
        point_id =transport_obj.point_id.id
        return {'value': {'old_point_id':point_id} , 'warning':warning}
            
    def root_transfer(self, cr, uid, ids, context=None):
        '''This method  transfer root of transportation 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : Dictionary 
        '''
        
        stu_prt_obj = self.pool.get('transport.participant')
        root_obj = self.pool.get('transport.registration')
        
        for new_data in self.browse(cr, uid, ids, context=context):
                part_data = stu_prt_obj.search(cr, uid, [('point_id', '=', new_data.old_point_id.id), ('name', '=', new_data.name.id)], context=context)
                stu_prt_obj.write(cr, uid, part_data, {'point_id' : new_data.new_point_id.id}, context=context)
                if new_data.old_point_id.id == new_data.new_point_id.id:
                    raise osv.except_osv(_('Error !'),_('Sorry you can select same point as before'))
                reg_data = root_obj.search(cr, uid, [('point_id', '=', new_data.old_point_id.id), ('part_name', '=', new_data.name.id)], context=context)
                root_obj.write(cr, uid, reg_data, {'point_id' : new_data.new_point_id.id}, context=context) 
        return {}
transfer_root()

