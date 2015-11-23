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

class transfer_vehicle(osv.TransientModel):
    _name = "transfer.vehicles"
    _description = "transfer vehicles"
    _columns = {
        'name':fields.many2one('student.student','Student Name', readonly=True),
        'participation_id':fields.many2one('transport.participant','Participation', required=True),
        'root_id':fields.many2one('student.transport','Root', required=True),
        'old_vehicle_id':fields.many2one('account.asset.asset','Old Vehicle No', required=True),
        'new_vehicle_id':fields.many2one('account.asset.asset','New Vehicle No', required=True),  
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
        result = super(transfer_vehicle, self).default_get(cr, uid, fields, context=context)
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
        @return : Dictionary having identifier of the record as key and the value of root 
        '''
        
        if transport:
            transport_obj = self.pool.get('transport.participant').browse(cr, uid, transport, context)
        return {'value': {'root_id': transport_obj.transport_id.id, 'old_vehicle_id': transport_obj.asset_id.id}}

    def vehicle_transfer(self, cr, uid, ids, context=None):
        '''This method  transfer vehicle of transportation 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : Dictionary 
        '''
        
        stu_prt_obj = self.pool.get('transport.participant')
        vehi_obj = self.pool.get('account.asset.asset')
        
        for new_data in self.browse(cr, uid, ids, context=context):
            vehi_data = vehi_obj.browse(cr, uid, new_data.old_vehicle_id.id, context=context)
            
            #check for transfer in same vehicle
            if new_data.old_vehicle_id.id == new_data.new_vehicle_id.id:
                raise osv.except_osv(_('Error !'),_('Sorry you can not transfer in same vehicle.'))
            
            # First Check Is there vacancy or not
            person = int(vehi_data.participant) + 1
            if vehi_data.capacity < person:
                raise osv.except_osv(_('Error !'),_('There is No More vacancy on this vehicle.'))
            stu_prt_obj.write(cr, uid, new_data.participation_id.id, {'asset_id': new_data.new_vehicle_id.id}, context=context)
            cr.execute("update vehicle_participant_student_rel set asset_id=%s where student_id=%s",(new_data.new_vehicle_id.id, new_data.participation_id.id))
        return {}

transfer_vehicle()
