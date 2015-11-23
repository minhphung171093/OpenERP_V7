# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import psycopg2
from openerp.osv import orm, fields
import xlrd
from base64 import b64decode
from openerp.tools.translate import _
from datetime import datetime, date, timedelta
import math


class dksquare_contract_import(orm.TransientModel):
    _inherit = 'base_import.import'
    _name = 'dksquare.contract.import'



    def do(self, cr, uid, ids,context=None):
        cr.execute('SAVEPOINT import')
        # contract_ids = self.pool.get('dk.contract').search(cr,uid,[])
        # self.pool.get('dk.contract').write(cr,uid,contract_ids,{'state':'progress'})
        record = self.browse(cr, uid, ids, context=context)[0]
        if record.file:
            workbook = xlrd.open_workbook(file_contents=b64decode(record.file))
            sheet = workbook.sheet_by_index(0)
            type_list = []
            for r in range(0,sheet.nrows):
                if r>=1:
                    row = sheet.row_values(r)
                    customer = row[1]
                    customer_obj = self.pool.get('res.partner')
                    customer_id = customer_obj.search(cr,uid,[('name','=',customer)])
                    if customer_id and len(customer_id)>0:
                        customer_id = customer_id[0]
                    else:
                        customer_add = row[2]

                        customer_tel = row[4]
                        customer_tel = customer_tel.split('/')
                        tel = customer_tel[0]
                        mobile=''
                        if len(customer_tel)>1:
                            mobile = customer_tel[1]
                        customer_id = customer_obj.create(cr,uid,{
                            'name':customer,
                            'street':customer_add,
                            'phone':tel,
                            'mobile':mobile,
                        })
                    ref_no = row[3]
                    type = row[5]
                    type_id = self.pool.get('dk.contract.type').search(cr,uid,[('name','=','type')])

                    if type_id and len(type_id)>0:
                        type_id = type_id[0]
                    else:
                        type_id = self.pool.get('dk.contract.type').create(cr,uid,{'name':type})
                    print 'type_id', type_id, type

                    qty = row[6]
                    start_date = row[7]
                    exp_date = row[8]
                    remarks = row[9]
                    last_svs_day = row[10]
                    schedule_date = row[11]
                    location = row[14]
                    location_obj = self.pool.get('dk.location')
                    location_id = location_obj.search(cr,uid,[('name','=',location)])
                    if location_id and len(location_id)>0:
                        location_id = location_id[0]
                    else:
                        location_id = location_obj.create(cr,uid,{'name':location})
                    note = row[15]
                    cheque_cash = row[16]
                    amount = row[17]
                    print 'schedule_date before',schedule_date
                    print 'last_svs_day before',last_svs_day
                    dk_contract_obj = self.pool.get('dk.contract')
                    if last_svs_day == '-' or not last_svs_day:
                        last_svs_day = False
                    if schedule_date == '-' or not schedule_date:
                        schedule_date = False

                    if last_svs_day:
                        last_svs_day = datetime(*xlrd.xldate_as_tuple(last_svs_day, workbook.datemode))
                    if schedule_date:
                        schedule_date = datetime(*xlrd.xldate_as_tuple(schedule_date, workbook.datemode))

                    print 'last_svs_day',last_svs_day
                    print 'schedule_date', schedule_date
                    new_contract = {
                                                    'partner_id':customer_id,
                                                    'ref_no':ref_no,
                                                    'type':type_id,
                                                    'qty':qty,
                                                    'start_date':start_date,
                                                    'exp_date':exp_date,
                                                    'remarks':remarks,
                                                    'last_svs_day':last_svs_day,
                                                    'schedule_date':schedule_date,
                                                    'location_id':location_id,
                                                    'note':note,
                                                    'cheque_cash':cheque_cash,
                                                    'amount':amount,
                    }
                    print 'new contract', new_contract
                    dk_contract_obj.create(cr,uid,new_contract)

        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return True


    def import_type(self, cr, uid, ids,context=None):
        cr.execute('SAVEPOINT import')
        # contract_ids = self.pool.get('dk.contract').search(cr,uid,[])
        # self.pool.get('dk.contract').write(cr,uid,contract_ids,{'state':'progress'})
        record = self.browse(cr, uid, ids, context=context)[0]
        if record.file:
            workbook = xlrd.open_workbook(file_contents=b64decode(record.file))
            sheet = workbook.sheet_by_index(0)
            type_list = []
            for r in range(0,sheet.nrows):
                if r>=1:
                    row = sheet.row_values(r)
                    type = row[13]
                    type_list.append(type)
            type_list = list(set(type_list))
            for type in type_list:
                self.pool.get('dk.contract.type').create(cr,uid,{'name':type})
        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return True


    def do2(self, cr, uid, ids,context=None):
        cr.execute('SAVEPOINT import')
        # contract_ids = self.pool.get('dk.contract').search(cr,uid,[])
        # self.pool.get('dk.contract').write(cr,uid,contract_ids,{'state':'progress'})
        record = self.browse(cr, uid, ids, context=context)[0]
        if record.file:
            workbook = xlrd.open_workbook(file_contents=b64decode(record.file))
            sheet = workbook.sheet_by_index(0)
            type_list = []
            for r in range(0,sheet.nrows):
                if r>=1:
                    row = sheet.row_values(r)
                    customer = row[0]
                    customer_obj = self.pool.get('res.partner')
                    customer_id = customer_obj.search(cr,uid,[('name','=',customer)])
                    city = row[8]
                    email = row[9]
                    if customer_id and len(customer_id)>0:
                        customer_id = customer_id[0]
                    else:
                        customer_add = row[1]
                        customer_id = customer_obj.create(cr,uid,{
                            'name':customer,
                            'street':customer_add,
                            'city':city,
                            'email':email,
                            })
                    type = row[13]
                    type_id = self.pool.get('dk.contract.type').search(cr,uid,[('name','=',type)])
                    if type_id and len(type_id)>0:
                        type_id = type_id[0]
                    else:
                        type_id = self.pool.get('dk.contract.type').search(cr,uid,[])[0].id

                    contact_person = row[2]
                    print 'contact_person_id', contact_person
                    contact_person_number = row[3]
                    location_of_service = row[4]
                    contact_person_id = customer_obj.search(cr,uid,[('name','=',contact_person)])
                    print 'contact_person_id', contact_person_id
                    if contact_person_id and len(contact_person_id)>0:
                        contact_person_id = contact_person_id[0]
                    else:
                        contact_person_id = customer_obj.create(cr,uid,{
                            'name':contact_person_id,
                            'street':location_of_service,
                            'phone':contact_person_number,

                            })

                    print 'contact_person_id', contact_person_id

                    start_date = row[5]
                    exp_date = row[6]

                    start_year = start_date[-2:]
                    start_month = start_date[:-3]
                    exp_year = exp_date[-2:]
                    exp_month = exp_date[:-3]

                    print 'exp_year' , exp_year
                    print 'exp_month ', exp_month

                    if start_month =='JAN':
                        start_month = '01'
                    elif start_month == 'FEB':
                        start_month = '02'
                    elif start_month == 'MAR':
                        start_month = '03'
                    elif start_month == 'APR':
                        start_month = '04'
                    elif start_month == 'MAY':
                        start_month = '05'
                    elif start_month == 'JUN':
                        start_month = '06'
                    elif start_month == 'JUL':
                        start_month = '07'
                    elif start_month == 'AUG':
                        start_month = '08'
                    elif start_month == 'SEP':
                        start_month = '09'
                    elif start_month == 'OCT':
                        start_month = '10'
                    elif start_month == 'NOV':
                        start_month = '11'
                    elif start_month == 'DEC':
                        start_month = '12'

                    if exp_month =='JAN':
                        exp_month = '01'
                    elif exp_month == 'FEB':
                        exp_month = '02'
                    elif exp_month == 'MAR':
                        exp_month = '03'
                    elif exp_month == 'APR':
                        exp_month = '04'
                    elif exp_month == 'MAY':
                        exp_month = '05'
                    elif exp_month == 'JUN':
                        exp_month = '06'
                    elif exp_month == 'JUL':
                        exp_month = '07'
                    elif exp_month == 'AUG':
                        exp_month = '08'
                    elif exp_month == 'SEP':
                        exp_month = '09'
                    elif exp_month == 'OCT':
                        exp_month = '10'
                    elif exp_month == 'NOV':
                        exp_month = '11'
                    elif exp_month == 'DEC':
                        exp_month = '12'

                    start_code = start_month + '/20'+start_year
                    exp_code = exp_month + '/20'+exp_year

                    print 'exp_code', exp_code
                    print 'start_code', start_code

                    start_date_ids = self.pool.get('account.period').search(cr,uid,[('code','=',start_code)])
                    exp_date_ids = self.pool.get('account.period').search(cr,uid,[('code','=',exp_code)])

                    start_period= None
                    exp_period = None

                    if start_date_ids and len(start_date_ids)>0:
                        start_period = start_date_ids[0]

                    if exp_date_ids and len(exp_date_ids)>0:
                        exp_period = exp_date_ids[0]


                    amount = row[7]
                    dk_contract_obj = self.pool.get('dk.contract')

                    new_contract = {
                        'partner_id':customer_id,
                        'type':type_id,
                        'start_date2':start_period,
                        'exp_date2':exp_period,
                        'amount':amount,
                        'state':'exp',
                        'location_of_service':location_of_service,
                        'contact_person_id':contact_person_id,
                        }
                    print 'new contract', new_contract
                    if customer_id and type_id and start_period and exp_period:
                        dk_contract_obj.create(cr,uid,new_contract)

        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return True



    def set_process_contact(self, cr, uid, ids, context=None):
        contract_ids = self.pool.get('dk.contract').search(cr,uid,[('state','in',['exp','renew'])])
        self.pool.get('dk.contract').write(cr,uid,contract_ids,{'state':'progress'})
        return True

    def change_period_contract(self,cr,uid,ids,context=None):
        contract_ids = self.pool.get('dk.contract').search(cr,uid,[])
        for contract in self.pool.get('dk.contract').browse(cr,uid,contract_ids):
            start_date = contract.start_date
            exp_date = contract.exp_date
            start_code = start_date[2:]+'/'+'20'+start_date[:-2]
            print 'start_code', start_code, start_date
            exp_code = exp_date[2:]+'/'+'20'+exp_date[:-2]
            print 'exp_code', exp_code, exp_date, contract.ref_no
        return True







    _columns = {

    }

dksquare_contract_import()