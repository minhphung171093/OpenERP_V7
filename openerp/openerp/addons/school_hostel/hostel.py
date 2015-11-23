# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hostel_type(osv.osv):
    
    _name = 'hostel.type'
    
    _columns = {
        'name': fields.char('Hostel Name', size=32, required=True),
        'type': fields.selection([('boys','Boys'),('girls','Girls'),('common','Common')], 'Hostel Type', required=True),
        'other_info': fields.text('Other Information'),
        'rector': fields.many2one('res.partner', 'Rector'),
        'room_ids': fields.one2many('hostel.room', 'name', 'Room'),
    }
    
    _defaults = {
            'type': 'common'
    }
hostel_type()

class hostel_room(osv.osv):
    
    _name = 'hostel.room'
    
    def _check_availability(self, cr, uid, ids, name, args, context=None):
        res = {}
        room_availability = 0
        for data in self.browse(cr, uid, ids, context):
            count = 0
            for student in data.student_ids:
                count += 1
            room_availability = data.student_per_room - count
#            if room_availability < 0:
#                raise osv.except_osv(("You can not assign room more than %s student" % data.student_per_room))
            res[data.id] = room_availability
        return res

    _columns = {
        'name': fields.many2one('hostel.type', 'Hostel'),
        'floor_no': fields.integer('Floor No.'),
        'room_no': fields.char('Room No.', size=128, required=True),
        'student_per_room': fields.integer('Student Per Room', required=True),
        'availability': fields.function(_check_availability, type='integer', string="Availability"),
        'student_ids': fields.one2many('hostel.student','hostel_room_id', 'Student'),
        'telephone' : fields.boolean ('Telephone access'),
        'ac' : fields.boolean ('Air Conditioning'),
        'private_bathroom' : fields.boolean ('Private Bathroom'),
        'guest_sofa' : fields.boolean ('Guest sofa-bed'),
        'tv' : fields.boolean ('Television'),
        'internet' : fields.boolean ('Internet Access'),
        'refrigerator' : fields.boolean ('Refrigerator'),
        'microwave' : fields.boolean ('Microwave'),
    }
    
    _defaults = {
            'floor_no': 1
    }
    _sql_constraints = [('room_no_unique', 'unique(room_no)', 'Room number must be unique!')]
    _sql_constraints = [('floor_per_hostel','check(floor_no < 10)','Error ! Floor per hostel should be less than 10.')]
    _sql_constraints = [('student_per_room_greater','check(student_per_room < 10)','Error ! Student per room should be less than 10.')]
    
hostel_room()

class hostel_student(osv.osv):
    
    _name = 'hostel.student'

    def _get_remaining_fee_amt(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        remaining_amount = 0.0
        for data in self.browse(cr, uid, ids, context):
            remaining_amount = data.room_rent - data.paid_amount
            res[data.id] = remaining_amount
        return res

    def confirm_state(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True

    def reservation_state(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'reservation'})
        return True

    def print_fee_receipt(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])[0]
        datas = {
            'ids': [data['id']],
            'form': data,
            'model':'hostel.student',
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'hostel_fee_slip', 'datas': datas}

    _columns = {
        'hostel_room_id': fields.many2one('hostel.room', 'Hostel Room'),
        'hostel_id': fields.char('Hostel ID', size=64, readonly=True),
        'student_id': fields.many2one('student.student', 'Student'),
        'school_id': fields.many2one('school.school', 'School'),
        'standard_id':fields.many2one('standard.standard', 'Class'),
        'division_id':fields.many2one('standard.division', 'Division'),
        'medium_id':fields.many2one('standard.medium', 'Medium'),
        'room_rent': fields.float('Total Room Rent', required=True),
        'bed_type' : fields.many2one('bed.type', 'Bed Type'),
#        'bed_type' : fields.selection((('gatch','Gatch Bed'),('electric','Electric'),('stretcher','Stretcher'),('low','Low Bed'),('low_air_loss','Low Air Loss'),('circo_electric','Circo Electric'),('clinitron','Clinitron')),'Bed Type', required=True),
        'admission_date': fields.datetime('Admission Date'),
        'discharge_date': fields.datetime('Discharge Date'),
        'paid_amount': fields.float('Paid Amount'),
        'remaining_amount': fields.function(_get_remaining_fee_amt, type='float', string='Remaining Amount'),
        'state': fields.selection([('draft','Draft'),('reservation','Reservation'),('confirm','Confirm')], 'State')
    }
    
    _defaults = {
            'state': 'draft',
            'hostel_id': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'hostel.student'),
    }
    
    _sql_constraints = [('admission_date_greater','check(discharge_date >= admission_date)','Error ! Discharge Date cannot be set before Admission Date.')]
    
    def onchange_student(self, cr, uid, ids, student_id, context=None):
        if student_id:
            student = self.pool.get('student.student').browse(cr, uid, student_id, context)
            return {'value':{'standard_id':student.standard_id.id,
                             'division_id':student.division_id.id,
                             'medium_id':student.medium_id.id,
                             'school_id':student.school_id.id}}
        return {}
hostel_student()

class bed_type(osv.osv):
    
    _name = 'bed.type'
    _description='Type of Bed in Hostel'
    
    _columns = {
        'name': fields.char('Name',required=True),
        'description': fields.text('Description'),
    }
bed_type()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=