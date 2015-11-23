 # coding=utf-8

#    Copyright (C) 2008-2010  Luis Falcon

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
from mx import DateTime
import datetime
from openerp.osv import fields, osv
from tools.translate import _

import sys


class hostel_registration (osv.osv):
       
    
# Method to check for availability and make the hostel bed reservation

    def registration_confirm(self, cr, uid, ids, context={}):
        ''' This method confirm hostel registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
         '''
        for reservation in self.browse(cr,uid,ids):
            bed_id= str(reservation.bed.id)
            cr.execute("select count (*) from student_hostel_registration where (admission_date::timestamp ,discharge_date::timestamp) overlaps ( timestamp %s , timestamp %s ) and state= %s and bed = cast(%s as integer)", (reservation.admission_date,reservation.discharge_date,'confirmed',bed_id))
            res = cr.fetchone()
    
        if res[0] > 0:
            raise osv.except_osv('Warning', 'Bed has been already reserved in this period' ) 
        else:
            self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def patient_discharge(self, cr, uid, ids, context={}):
        ''' This method Discharge student in hostel.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
         '''
        self.write(cr, uid, ids, {'state':'free'})
        return True

    def registration_cancel(self, cr, uid, ids, context={}):
        ''' This method cancel hostel registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
         '''
        self.write(cr, uid, ids, {'state':'cancelled'})
        return True

    def registration_admission(self, cr, uid, ids, context={}):
        ''' This method done hostel registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
         '''
        self.write(cr, uid, ids, {'state':'done'})
        return True
    
    _name = "student.hostel.registration"
    _table = "student_hostel_registration"
    _rec_name="user_id"
    _description = "Student Admission History"
    _columns = {
        'user_id': fields.many2one('student.student', 'Student', required=True, ondelete="cascade", select=True),
        'reg_code' : fields.char ('Registration Code',size=128),
        'admission_date' : fields.datetime ('Admission date'),
        'discharge_date' : fields.datetime ('Discharge date'),
        'rector':fields.many2one('hr.employee', 'Rector'),
        'bed' : fields.many2one ('student.hostel.bed','Room Detail'),
        'info' : fields.text ('Extra Info'),
        'state': fields.selection((('free','Free'),('cancelled','Cancelled'),('confirmed','Confirmed'),('done','Got Admission')),'Status'),
        }

    _defaults = {
        'reg_code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'student.hostel.registration'),
        'state': lambda *a : 'free'
    }

    _sql_constraints = [
                ('name_uniq', 'unique (reg_code)', 'The Registration code already exists')]

hostel_registration ()
    
class hostel_building (osv.osv):
    
    _name = "student.hostel.building"
    _columns = {
        'name' : fields.char ('Name', size=128, help="Name of the building within the institution"),
        'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
        'code' : fields.char ('Code', size=64),
        'extra_info' : fields.text ('Extra Info'),
        }
hostel_building ()

class hospital_ward (osv.osv):
    
    _name = "student.hostel.rooms"
    _table="student_hostel_rooms"
    _columns = {
        'name' : fields.char ('Name', size=128, help="Ward / Room code"),
        'institution' : fields.many2one ('res.partner','Institution',help="Medical Center"),
        'floor' : fields.integer ('Floor Number'),
        'private' : fields.boolean ('Private',help="Check this option for private room"),
        'number_of_beds' : fields.integer ('Number of beds',help="Number of beds per Room"),
        'telephone' : fields.boolean ('Telephone access'),
        'ac' : fields.boolean ('Air Conditioning'),
        'private_bathroom' : fields.boolean ('Private Bathroom'),
        'guest_sofa' : fields.boolean ('Guest sofa-bed'),
        'tv' : fields.boolean ('Television'),
        'internet' : fields.boolean ('Internet Access'),
        'refrigerator' : fields.boolean ('Refrigerator'),
        'microwave' : fields.boolean ('Microwave'),
        'gender' : fields.selection ((('men','Boys Hostel'),('women','Girls Hostel')),'Gender', required=True),
        'state': fields.selection((('beds_available','Beds available'),('full','Full'),('na','Not available')),'Status'),
        'extra_info' : fields.text ('Extra Info'),
        }

hospital_ward ()

class hospital_bed (osv.osv):

    _name = "student.hostel.bed"
    _rec_name = 'name'
    _columns = {
        'name' : fields.many2one ('product.product','Bed', help="Bed Number"),
        'ward' : fields.many2one ('student.hostel.rooms','Ward',help="Ward or room"),
        'bed_type' : fields.selection((('gatch','Gatch Bed'),('electric','Electric'),('stretcher','Stretcher'),('low','Low Bed'),('low_air_loss','Low Air Loss'),('circo_electric','Circo Electric'),('clinitron','Clinitron')),'Bed Type', required=True),
        'telephone_number' : fields.char ('Telephone Number',size=128, help="Telephone number / Extension"),
        'extra_info' : fields.text ('Extra Info'),
        'state': fields.selection((('free','Free'),('reserved','Reserved'),('occupied','Occupied'),('na','Not available')),'Status'),
        }

    _defaults = {
                'bed_type': lambda *a: 'gatch',
        }
hospital_bed ()