# -*- coding: utf-8 -*-

__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from datetime import datetime
import calendar
from openerp.tools.translate import _

class dk_contract(osv.osv):
    _name = 'dk.contract'

    def write(self, cr, uid, ids, vals, context={}):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('schedule_date'):
            vals['cpl_date']=vals.get('schedule_date')
            for id in ids:
                now = datetime.now()
                current_period_id = self.pool.get('account.period').search(cr,uid,[('date_start','<=',now),('date_stop','>=',now)])
                remark_id = self.pool.get('dk.remark').search(cr,uid,[('contract_id','=',id),('period_id','=',current_period_id)])
                self.pool.get('dk.remark').write(cr,uid,remark_id,{'date':vals.get('schedule_date')})

        if vals.get('last_svs_day'):
            for id in ids:
                self.pool.get('dk.last_svs_date').create(cr,uid,{'contract_id':id,
                                                                 'last_sys_date':vals.get('last_svs_day')})

        if not context.get('non_log'):

            for id in ids:
                self.pool.get('dk.edit_history').create(cr,uid,{'contract_id':id,
                                                                'date':datetime.now(),
                                                                'user_id':uid})


        return super(dk_contract,self).write(cr,uid,ids,vals,context)


    def create(self, cr, uid, vals, context=None):
        period_id = self._get_period(cr, uid, context)
        fy = False
        c = {}
        if period_id:
            fy = self.pool.get('account.period').browse(cr, uid, period_id).fiscalyear_id.id
            c = {'fiscalyear_id': fy}
        obj_sequence = self.pool.get('ir.sequence')
        seq = obj_sequence.next_by_code(cr, uid, 'dk.contract.seq', context=c)
        vals.update({'ref_no':seq})
        return super(dk_contract, self).create(cr, uid, vals, context)
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['ref_no'], context=context)
        res = []
        for record in reads:
            name = '/'
            if record['ref_no']:
                name = record['ref_no']
            res.append((record['id'], name))
        return res

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False

    def _get_ref_no(self, cr, uid, context=None):
        cr.execute('select "ref_no" ,"id" from "dk_contract" order by "id" desc limit 1')
        id_returned = cr.fetchone()
        print 'id_returned', id_returned
        number = '0'
        if id_returned:
            number = id_returned[0].split('/')
        next = 0
        if len(number)>1:
            current = number[1]
            next = int(current)+1
        if next>0:
            return number[0]+'/'+str(next)
        else:
            return '/'


    def onchange_ref_no(self, cr, uid, ids, ref_no, context={}):
        return {'value': {'ref_no2': ref_no}}

    def onchange_company_id(self, cr, uid, ids, company_id, context={}):
        company_obj = self.pool.get('res.company').browse(cr,uid,company_id)
        print 'in on change company'
        if company_obj.company_gst_type=='inclusive':
            print 'return inclusive'
            return {'value': {'gst_type2': ' inclusive of GST'}}
        elif company_obj.company_gst_type=='exclusive':
            print 'return exclusive'
            return {'value': {'gst_type2': ' exclusive of GST'}}

    def onchange_partner_id(self, cr, uid, ids, partner_id, context={}):
        value = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            if len(partner.child_ids)>0:
                value['attn_id']= partner.child_ids[0].id
                value['contact_person_id'] = partner.child_ids[0].name
                value['contact_person_phone'] = partner.child_ids[0].phone
                value['contact_email'] = partner.child_ids[0].email
                value['location_of_service'] = 'AS ABOVE ADDRESS'
            else:
                value['attn_id']= None
            value['street']=partner.street
            value['street2']=partner.street2
            value['country_id']=partner.country_id.id
            value['city']=partner.city
            value['state_id']=partner.state_id.id
            value['zip']=partner.zip
            value['email']=partner.email
            value['partner_is_company'] = partner.is_company

        return {'value':value}


    #
    # def onchange_contact_person_id(self, cr, uid, ids, contact_person_id,partner_id, context={}):
    #     value = {}
    #     if contact_person_id==partner_id:
    #         value['location_of_service'] = 'AS ABOVE ADDRESS'
    #     else:
    #         add =  self.pool.get('res.partner')._display_address(cr, uid, self.pool.get('res.partner').browse(cr,uid,contact_person_id), without_company=True, context=context)
    #         value['location_of_service'] = add
    #     if contact_person_id:
    #         contact_person = self.pool.get('res.partner').browse(cr,uid,contact_person_id)
    #         value['contact_person_phone'] = contact_person.phone
    #         value['contact_email'] = contact_person.email
    #     return {'value': value}


    def onchange_date_order(self, cr, uid, ids, date_order, context={}):
        return {'value': {'date_order2': date_order}}

    def onchange_type(self, cr, uid, ids, type, context={}):
        return {'value': {'contract_type2': type}}

    def action_view_invoice(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_dksquare_invoice_action')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        # compute the number of invoices to display
        inv_ids = self.pool.get('account.invoice').search(cr, uid, [('contract_id', 'in', ids)])
        #choose the view_mode accordingly
        if len(inv_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_dksquare_invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
            print 'result ', result
        return result


    def action_view_renew_contract(self, cr, uid, ids, context=None):
        print 'in here action_view_renew_contract'
        res = {}
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_dksquare_contract_paper_form')
        view_id = view_ref and view_ref[1] or False,
        inv_ids = self.pool.get('dk.contract').search(cr, uid, [('source_contract_id', 'in', ids)])
        print 'source_contract_id ', inv_ids, ids
        if len(inv_ids) > 0:
            res = {
                   'type': 'ir.actions.act_window',
                   'name': 'Renewed Contract',
                   'view_mode': 'form',
                   'view_type': 'form',
                   'view_id': view_id,
                   'res_model': 'dk.contract',
                   'nodestroy': True,
                   'res_id': inv_ids[0], # assuming the many2one
                   'target':'current',
                   'context': context,
                 }
        return res



    def active_contract(self,cr,uid,ids,context=None):
        for contract in self.browse(cr,uid,ids,context):
            if contract.source_contract_id:
                self.write(cr,uid,contract.source_contract_id.id,{'state':'invalid'})
                self.pool.get('dk.comment').create(cr,uid,{'remarks': contract.ref_no + ' Renew Deactive',
                                                           'contract_id':contract.source_contract_id.id})
            self.check_contract_type_fomula(cr,uid,ids)
            self.check_schedule_date_new(cr,uid,contract.id)
        self.write(cr,uid,ids,{'state':'valid','just_renew':False})
        return True

    def change_form_view(self,cr,uid,ids,context=None):
        mod, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_construction_dk_contract_form_view')
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dk.contract',
            'type': 'ir.actions.act_window',
            'res_id': ids[0],
            'view_id': view_id,
            'target': 'current',
            'context': context,
            'nodestroy': True,
        }

    def change_paper_view(self,cr,uid,ids,context=None):
        mod, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_dksquare_contract_paper_form')
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dk.contract',
            'type': 'ir.actions.act_window',
            'res_id': ids[0],
            'view_id': view_id,
            'target': 'current',
            'context': context,
            'nodestroy': True,
        }


    def deactive_contract(self,cr,uid,ids,context=None):
        if context is None:
            context = {}

        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'remark.notice',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

    def create_appointment(self,cr,uid,ids,context=None):
        for contract in self.browse(cr,uid,ids):

            if contract.schedule_date:
                location_of_service=''
                if contract.location_of_service=='AS ABOVE ADDRESS':
                    location_of_service = str(contract.street) + ' ' + str(contract.street2) + ' '+ str(contract.city)  + ' '+  str(contract.zip)
                else:
                    location_of_service=contract.location_of_service

                new_appointment_id = self.pool.get('package.booking').create(cr,uid,{'partner_id':contract.partner_id.id,
                                                                'user_id':uid,
                                                                'date':contract.schedule_date,
                                                                'contract_id':contract.id,
                                                                'location_of_service':location_of_service,

                                                                })

                mod, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_DK_Square', 'saicoms_package_booking_form')

                return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'package.booking',
                'type': 'ir.actions.act_window',
                'res_id': new_appointment_id,
                'target': 'current',
                'context': context,
                'nodestroy': True,
                }
            else:
                raise osv.except_osv(_('No Schedule date set!'),_("You have to assign schedule date to create appointment!"))

    def action_button_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'manual'})
        user_uid = uid
        for contract in self.browse(cr, uid, ids):
            uid = 1
            invoice_obj = self.pool.get('account.invoice')
            partner_id = contract.partner_id
            defaults = invoice_obj._defaults
            type = invoice_obj._get_type(cr, uid, context)
            reference_type = defaults['reference_type']
            journal_id = invoice_obj._get_journal(cr, uid, context)
            user = self.pool.get('res.users').browse(cr, 1, user_uid, context=context)
            company_id = contract.company_id.id
            currency_id = invoice_obj._get_currency(cr, uid, context)
            state = defaults['state']
            user_id = user.id
            dk_subject = defaults['dk_subject']
            sent = False
            onchange_info = \
            invoice_obj.onchange_partner_id(cr, uid, False, type, partner_id.id, False, False, False, company_id)[
                'value']
            fiscal_position = onchange_info['fiscal_position']
            account_id = onchange_info['account_id']
            payment_term = onchange_info['payment_term']
            invoice = invoice_obj.create(cr, uid, {'type': type,
                                                   'partner_id': partner_id.id,
                                                   'contract_id': contract.id,
                                                   'origin': contract.ref_no,
                                                   'reference_type': reference_type,
                                                   'journal_id': journal_id,
                                                   'company_id': company_id,
                                                   'dk_company_id': company_id,
                                                   'currency_id': currency_id,
                                                   'state': state,
                                                   'user_id': user_id,
                                                   'dk_subject': dk_subject,
                                                   'fiscal_position': fiscal_position,
                                                   'account_id': account_id,
                                                   'payment_term': payment_term,
                                                   'sent': sent})

            if invoice:
                invoice_line_id = self.pool.get('account.invoice.line').create(cr, uid, {'invoice_id': invoice,
                                                                                         'name': 'Invoice of contract %s' % contract.ref_no,
                                                                                         'quantity': 1,
                                                                                         'price_unit': contract.amount,
                })
                if invoice_line_id:
                    self.write(cr, uid, contract.id, {'invoice_exists': True})

        self.create_default_remark(cr,uid,ids)
        self.check_contract_type_fomula(cr,uid,ids)
        return True

    def check_schedule_date(self, cr, uid, id, context=None):
        has_schedule = False
        contract = self.browse(cr, uid, id)
        if contract.type.name == 'M':
            self.write(cr, uid, contract.id, {'has_schedule_date': True})
            has_schedule = True
        else:
            remarks = contract.remarks
            if remarks:
                start_month = contract.start_date2.date_start[5:7]
                exp_month = contract.exp_date2.date_start[5:7]
                remark_month = remarks.split('/')
                remark_month.append(start_month)
                remark_month.append(exp_month)
                month = datetime.now().month
                if str(month) in remark_month:
                    self.write(cr, uid, contract.id, {'has_schedule_date': True})
                    has_schedule = True
                else:
                    self.write(cr, uid, contract.id, {'has_schedule_date': False})
                    has_schedule = False
            else:
                has_schedule = False
                self.write(cr, uid, contract.id, {'has_schedule_date': False})
        return has_schedule

    def check_schedule_date_new(self, cr, uid, id, context=None):
        has_schedule = False
        contract = self.browse(cr, uid, id)
        now = datetime.now()
        current_period_id = self.pool.get('account.period').search(cr,uid,[('date_start','<=',now),('date_stop','>=',now)])
        remark_id = self.pool.get('dk.remark').search(cr,uid,[('contract_id','=',id),('period_id','=',current_period_id),('have_schedule','=',True)])
        if remark_id:
            has_schedule = True
            self.write(cr, uid, contract.id, {'has_schedule_date': True})
        else:
            has_schedule = False
            self.write(cr, uid, contract.id, {'has_schedule_date': False})
        return has_schedule

    def set_contract_state(self,cr,uid,ids,context=None):
        contract_ids = self.search(cr,uid,[('state','=',None)])
        self.write(cr,uid,contract_ids,{'state':'progress'})
        contract_ids = self.search(cr,uid,[('company_id','=',None)])
        self.write(cr,uid,contract_ids,{'company_id':1})

    def test_generate_schedule_date(self, cr, uid, ids, context=None):
        uid = 1
        today = datetime.now().day
        contract_cpl_ids=self.search(cr,uid,[('cpl_date','=',datetime.now().date())])
        self.write(cr,uid,contract_cpl_ids,{'last_svs_day':datetime.now().date()})
        contract_ids = self.search(cr, uid, [('state', '=', 'valid')])
        for contract in self.browse(cr, uid, contract_ids):
            has_schedule = self.check_schedule_date_new(cr, uid, contract.id, context)
            if has_schedule:
                self.write(cr, uid, contract.id, {'schedule_date': None})
            if not has_schedule and contract.schedule_date:
                    self.write(cr,uid,contract.id,{'last_svs_day':contract.schedule_date,
                                                   'schedule_date':None})
        return True

    def create_default_remark(self, cr, uid, ids, context=None):
        for contract in self.browse(cr,uid,ids,context):
            old_remark_ids = map(lambda x:x.id, contract.remark_ids)
            self.pool.get('dk.remark').unlink(cr,uid,old_remark_ids)
            period_ids = self.pool.get('account.period').search(cr,uid,[('date_stop','<=',contract.exp_date2.date_stop),('date_start','>=',contract.start_date2.date_start),('company_id','=',contract.company_id.id)])
            for period in self.pool.get('account.period').browse(cr,uid,period_ids):
                if period.code[0:2]!='00':
                    self.pool.get('dk.remark').create(cr,uid,{'contract_id':contract.id,
                                                              'period_id':period.id})
        return True

    def check_contract_type_fomula(self, cr, uid, ids, context=None):
        remark_obj = self.pool.get('dk.remark')
        for contract in self.browse(cr,uid,ids,context):
            remark_ids = map(lambda x:x.id, contract.remark_ids)
            period_ids = map(lambda x:x.period_id.id, self.pool.get('dk.remark').browse(cr,uid,remark_ids))
            remark_obj.write(cr,uid,remark_ids,{'have_schedule':False})

            if contract.type.name =='M':
                remark_obj.write(cr,uid,remark_ids,{'have_schedule':True})
            elif contract.type.name=='Q' or contract.type.name=='4/Q':
                remark_Q_ids = [remark for remark in remark_ids if remark_ids.index(remark)%3==0]
                remark_obj.write(cr,uid,remark_Q_ids,{'have_schedule':True})

            elif contract.type.name=='6/E':
                remark_6E_ids=[]
                mod = 0
                for remark in self.pool.get('dk.remark').browse(cr,uid,remark_ids):
                    # if remark_ids.index(remark.id)==0:
                    #     mod = int(remark.period_id.code[0:2])%2
                    #     remark_6E_ids.append(remark.id)
                    # if remark_ids.index(remark.id) not in [0,1]:
                    #     if remark_ids.index(remark.id)%2==mod:
                    #         remark_6E_ids.append(remark.id)
                    mod = int(remark.period_id.code[0:2])%2
                    if mod == 0:
                        remark_6E_ids.append(remark.id)
                remark_obj.write(cr,uid,remark_6E_ids,{'have_schedule':True})

            elif contract.type.name=='6/O':
                remark_6E_ids=[]
                mod = 0
                for remark in self.pool.get('dk.remark').browse(cr,uid,remark_ids):
                    # if remark_ids.index(remark.id)==0:
                    #     mod = int(remark.period_id.code[0:2])%2
                    #     remark_6E_ids.append(remark.id)
                    # if remark_ids.index(remark.id) not in [0,1]:
                    #     if remark_ids.index(remark.id)%2!=mod:
                    #         remark_6E_ids.append(remark.id)
                    mod = int(remark.period_id.code[0:2])%2
                    if mod == 1:
                        remark_6E_ids.append(remark.id)
                remark_obj.write(cr,uid,remark_6E_ids,{'have_schedule':True})

            elif contract.type.name=='4/E':
                remark_6E_ids=[]
                for remark in self.pool.get('dk.remark').browse(cr,uid,remark_ids):
                    if remark_ids.index(remark.id)==0 or remark_ids.index(remark.id)==1:
                        if remark.id not in remark_6E_ids and int(remark.period_id.code[0:2])%2==0:
                            remark_6E_ids.append(remark.id)
                    if remark_ids.index(remark.id)%3==0 or remark_ids.index(remark.id)%3==1:
                        if remark.id not in remark_6E_ids and int(remark.period_id.code[0:2])%2==0:
                            remark_6E_ids.append(remark.id)
                remark_obj.write(cr,uid,remark_6E_ids,{'have_schedule':True})

            elif contract.type.name=='4/O':
                remark_6E_ids=[]
                for remark in self.pool.get('dk.remark').browse(cr,uid,remark_ids):
                    if remark_ids.index(remark.id)==0 or remark_ids.index(remark.id)==1:
                        if remark.id not in remark_6E_ids and int(remark.period_id.code[0:2])%2==1:
                            remark_6E_ids.append(remark.id)
                    if remark_ids.index(remark.id)%3==0 or remark_ids.index(remark.id)%3==1:
                        if remark.id not in remark_6E_ids and int(remark.period_id.code[0:2])%2==1:
                            remark_6E_ids.append(remark.id)
                remark_obj.write(cr,uid,remark_6E_ids,{'have_schedule':True})

            elif contract.type.name=='2/Y':
                remark_6E_ids=[]
                for remark in self.pool.get('dk.remark').browse(cr,uid,remark_ids):
                    if remark_ids.index(remark.id)%6==0:
                        remark_6E_ids.append(remark.id)
                remark_obj.write(cr,uid,remark_6E_ids,{'have_schedule':True})

            elif contract.type.name=='3/Q':
                remark_Q_ids = [remark for remark in remark_ids if remark_ids.index(remark)%4==0]
                remark_obj.write(cr,uid,remark_Q_ids,{'have_schedule':True})


        return True


    def generate_schedule_date(self, cr, uid, context=None):
        uid = 1
        today = datetime.now().day
        contract_cpl_ids=self.search(cr,uid,[('cpl_date','=',datetime.now().date())])
        self.write(cr,uid,contract_cpl_ids,{'last_svs_day':datetime.now().date()})
        contract_ids = self.search(cr, uid, [('state', '=', 'progress')])
        if today == 1:
            for contract in self.browse(cr, uid, contract_ids):
                has_schedule = self.check_schedule_date_new(cr, uid, contract.id, context)
                if has_schedule:
                    self.write(cr, uid, contract.id, {'schedule_date': None})
                if not has_schedule and contract.schedule_date:
                    self.write(cr,uid,contract.id,{'last_svs_day':contract.schedule_date,
                                                   'schedule_date':None})

        return True

    def set_exp_contact(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'exp'})
        return True


    def test_check_exp_contract(self, cr, uid,ids, context=None):
        uid = 1
        today = datetime.now()
        contract_ids = self.search(cr, uid, [('exp_date2.date_stop','<=',today)])
        self.write(cr, uid, contract_ids , {'state': 'exp'})
        return True


    def add_months(sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)


    def check_exp_contract(self, cr, uid, context=None):
        uid = 1
        today = datetime.now()
        if today.day == 1:
            contract_ids = self.search(cr, uid, [('exp_date2.date_stop','<=',today)])
            self.write(cr, uid, contract_ids , {'state': 'exp',
                                                'expiring':False,})
            next_month = self.add_months(today,1)
            expring_contract_ids = self.search(cr, uid, [('state', '=', 'valid'),('exp_date2.date_stop','<=',next_month)])
            for contract in self.browse(cr, uid, expring_contract_ids, context):
                self.write(cr, uid, contract.id, {'expiring': True})
        return True

    def renew_button(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context):
            if contract.state in ('exp','valid'):
                ref_no  = self._get_ref_no(cr, uid)
                date_order = datetime.now()
                new_contract = self.copy(cr, uid, contract.id, {'ref_no': ref_no,
                                                                'ref_no2':ref_no,
                                                                'start_date':contract.start_date2,
                                                                'exp_date':contract.exp_date2,
                                                                'state':'draft',
                                                                'last_svs_day':None,
                                                                'schedule_date':None,
                                                                'source_contract_id':contract.id,
                                                                'just_renew':True,
                                                                'date_order': date_order,
                                                                }, context)
                self.write(cr,uid,contract.id,{'just_renew':True})
                view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_DK_Square', 'tgb_dksquare_contract_paper_form')
                view_id = view_ref and view_ref[1] or False,
                return {
                           'type': 'ir.actions.act_window',
                           'name': 'New Contract',
                           'view_mode': 'form',
                           'view_type': 'form',
                           'view_id': view_id,
                           'res_model': 'dk.contract',
                           'nodestroy': True,
                           'res_id': new_contract, # assuming the many2one
                           'target':'current',
                           'context': context,
                }

    def send_reminder_button(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'just_renew':False})
        return True



    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        return company_id

    def _get_default_gst_type(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        if company_id.company_gst_type =='inclusive':
            return ' inclusive of GST'
        elif company_id.company_gst_type =='exclusive':
            return ' exclusive of GST'

    def _get_default_appoint_holder(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr,uid,uid).partner_id.id
        return company_id

    def _get_contract_valid(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = 'no'
            if record.state =='valid':
                res[record.id]='yes'
        return res



    def _get_street_tree(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ''
            if record.location_of_service =='AS ABOVE ADDRESS':
                res[record.id]=str(record.street) + ' ' + str(record.street2) + ' '+ str(record.city)  + ' '+  str(record.zip)
            else:
                res[record.id]=record.location_of_service
        return res


    def _get_remark_tree(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            return_remarks = ''
            for remark in record.remark_ids:
                if remark.have_schedule:
                    return_remarks+=remark.period_id.code[0:2]+'/'
            res[record.id] = return_remarks[:-1]
        return res


    def _get_gst_type(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.company_id.company_gst_type == 'inclusive':
                res[record.id] = 'inclusive of GST'
            elif record.company_id.company_gst_type=='exclusive':
                res[record.id] = 'exclusive of GST'
        return res

    def _get_gst_amount(self,cr,uid,ids,name,arg,context=None):
        res={}
        for record in self.browse(cr,uid,ids):
            if record.amount:
                res[record.id] = record.amount*7/100 + record.amount
        return res

    def _get_amount_balance(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id]={}
            balance = record.amount-record.cheque_cash2
            res[record.id]['amount_balance'] = balance
            if balance == 0:
                res[record.id]['color_code'] = 1
            elif balance == record.amount:
                res[record.id]['color_code'] = -1
            else:
                res[record.id]['color_code'] = 0
        return res



    def _get_schedule_tree(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ''
            if not record.schedule_date:
                if record.has_schedule_date:

                    res[record.id]=record.schedule_date
                else:
                    res[record.id]="NIL"
            else:
                schedule_date = record.schedule_date
                year = schedule_date[0:4]
                month = schedule_date[5:7]
                day = schedule_date[8:10]
                res[record.id]=month+'/'+day+'/'+year
                # res[record.id]= record.schedule_date
        return res



    def _get_currency_id(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        currency_id = self.pool.get('account.invoice')._get_currency(cr, uid, context)
        return currency_id

    _columns = {
        'last_svs_date_ids':fields.one2many('dk.last_svs_date','contract_id','Last Service Date'),
        'user_edit_history_ids':fields.one2many('dk.edit_history','contract_id','User Edit History'),
        'remark_ids':fields.one2many('dk.remark','contract_id','Remarks'),
        'attn_id':fields.many2one('res.partner','Attn '),
        'currency_id':fields.many2one('res.currency'),
        'date_order': fields.date('Date', required=True, readonly=True, select=True,
                                  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'date_order2': fields.date('Date', required=True, readonly=True, select=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', string='Customer', domain=[('customer', '=', True)],
                                      required=True),
        'partner_is_company':fields.related('partner_id','is_company',type='boolean',string='This partner is company?'),
        'street': fields.related('partner_id', 'street', string='Street', readonly=True, type='char'),
        'street2': fields.related('partner_id', 'street2', string='Street', readonly=True, type='char'),
        'city': fields.related('partner_id', 'city', string='City', readonly=True, type='char'),
        'state_id': fields.related('partner_id', 'state_id', string='State', readonly=True, type='many2one',
                                   relation='res.country.state'),
        'country_id': fields.related('partner_id', 'country_id', string='Country', readonly=True, type='many2one',
                                     relation='res.country'),
        'zip': fields.related('partner_id', 'zip', string='Zip', readonly=True, type='char'),
        'ref_no': fields.char('Ref No', size=20, required=True),
        'per_annum': fields.char('Per Annum', size=20, required=True),
        'ref_no2': fields.char('Ref No', size=20),
        'phone': fields.related('partner_id', 'phone', string='Phone', type='char'),
        'mobile': fields.related('partner_id', 'mobile', string='Hand Phone', type='char'),
        'email': fields.related('partner_id', 'email', type='char', string='Email', readonly=True),
        'type': fields.many2one('dk.contract.type', 'Type', required=True),
        'qty': fields.char('Qty', size=50, ),
        'start_date': fields.char('Start', size=4, required=False),
        'exp_date': fields.char('EXP', size=4, required=False),
        'start_date2': fields.many2one('account.period','Start',required=True,),
        'exp_date2': fields.many2one('account.period','EXP',required=True),
        'remarks': fields.text('Remarks'),
        'location_of_service': fields.char('Location of Service',size=255),
        'contract_term': fields.text('Contract Terms'),
        'last_svs_day': fields.date('Last SVS Date', ),
        'schedule_date': fields.date('SCH Date', ),
        'schedule_date_readonly':fields.char('SCH Date',size=1),
        'cpl_date': fields.date('CPL Date', ),
        'attend': fields.char('Attend', size=100, ),
        'location_id': fields.many2one('dk.location', string='Location'),
        'note': fields.text('Take Note', ),
        'cheque_cash': fields.char('Check/Cash', size=100, ),
        'cheque_cash2': fields.float('Check/Cash', digits_compute=dp.get_precision('Account'),),
        'amount_balance':fields.function(_get_amount_balance,type='float',string="Balance", store={
                                            _name: (lambda self, cr,uid,ids,c: ids, ['cheque_cash2','amount'], 10),
                                            },multi='balance'),
        'color_code':fields.function(_get_amount_balance,type='float',string="color code", store={
                                            _name: (lambda self, cr,uid,ids,c: ids, ['cheque_cash2','amount'], 10),
                                            },multi='balance'),
        'amount': fields.float('AMT', digits_compute=dp.get_precision('Account'), required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True, ),
        'company_id': fields.many2one('res.company', 'Contract Company', required=True),
        'invoice_exists': fields.boolean('Invoice Exists'),
        'state': fields.selection([
                                      ('draft', 'Draft Quotation'),
                                      ('sent', 'Quotation Sent'),
                                      ('cancel', 'Cancelled'),
                                      ('valid', 'Valid'),
                                      ('invalid', 'InValid'),
                                      ('waiting_date', 'Waiting Schedule'),
                                      ('progress', 'To Contract'),
                                      ('manual', 'To Invoice'),
                                      ('invoice_except', 'Invoice Exception'),
                                      ('exp', 'Expired'),
                                      ('renew', 'Renewed'),
                                  ], 'Status', readonly=True, track_visibility='onchange',
                                  help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.",
                                  select=True),

        'gst_type_select': fields.selection([
                                      ('inclusive', 'inclusive of GST'),
                                      ('exclusive', 'exclusive of GST'),
                                  ], 'Status', select=True),

        'street_tree':fields.function(_get_street_tree,type='char',string="Location of Service", store=False),
        'remark_tree':fields.function(_get_remark_tree,type='char',string="Remarks", store=False),
        'schedule_tree':fields.function(_get_schedule_tree,type='char',string="Schedule Date", store=False),
        'contract_valid':fields.function(_get_contract_valid,type='selection',selection= [('yes','Yes'),('no','No')],string="Valid",store={
            _name: (lambda self, cr,uid,ids,c: ids, ['state'], 10),
            }),
        'dk_company_logo': fields.related('company_id', 'logo_web', type='binary', string='logo'),
        'dk_company_name': fields.related('company_id', 'name', type='char', string='name', readonly=True),
        'dk_company_street': fields.related('company_id', 'street', type='char', string='street', readonly=True),
        'dk_company_street2': fields.related('company_id', 'street2', type='char', string='street', readonly=True),
        'dk_company_city': fields.related('company_id', 'city', type='char', string='city', readonly=True),
        'dk_company_zip': fields.related('company_id', 'zip', type='char', string='zip', readonly=True),
        'dk_company_state': fields.related('company_id', 'state_id', type='many2one',relation='res.country.state', string='state', readonly=True),
        'dk_company_country': fields.related('company_id', 'country_id', type='many2one',relation='res.country', string='country', readonly=True),
        'dk_company_phone': fields.related('company_id', 'phone', type='char', string='phone', readonly=True),
        'dk_company_fax': fields.related('company_id', 'fax', type='char', string='fax', readonly=True),
        'dk_company_email': fields.related('company_id', 'email', type='char', string='Email', readonly=True),
        'dk_company_rml_report_footer': fields.related('company_id', 'rml_footer_readonly', type='text', readonly=True),
        'contract_type2': fields.many2one('dk.contract.type', string='Type'),
        'dk_bank_cheque_no': fields.char('BANK/ CHEQUE No', size=128),
        'dk_bank_cheque_amount': fields.float('bank check amount', digits_compute=dp.get_precision('Account'), ),
        'dk_bank_date': fields.date('DATE'),
        'contact_person_id': fields.char('Contact Person',size=255),
        'contact_person_phone': fields.char(string='Contact No',size=266),
        'contact_email':fields.char( string='Email', size=255),
        'dk_subject': fields.char('Subject', size=255),
        'appoint_holder': fields.many2one('res.partner', 'Appointment Holder', domain=[('customer','=',False),('supplier','=',False),('is_company','=',False)] ),
        'assign_user':fields.many2one('res.users','Assign User'),
        'appoint_holder_phone': fields.related('appoint_holder', 'phone', type='char', string='HP', readonly=True),
        'has_schedule_date': fields.boolean('Has Schedule In this Month'),
        'dk_tax_id': fields.related('company_id', 'dk_tax_id', type="many2many", relation='account.tax', string='Taxes',
                                    readonly=True),
        'use_tax': fields.related('company_id', 'use_tax', type='boolean', string='Use Tax', readonly=True),
        'expiring': fields.boolean('Expiring in 1 month'),
        'source_contract_id':fields.many2one('dk.contract','Source Contract'),
        'just_renew':fields.boolean('Just renewed',),
        'just_remind':fields.boolean('Just remind',),
        'dk_comment_ids':fields.one2many('dk.comment','contract_id','Comments'),
        'gst_type':fields.function(_get_gst_type,type='char',string="GST Type", store=False),
        'gst_type2':fields.char('GST TYpe', size=128),
        'gst_amount_is':fields.char('gst amount is',size=128),
        'gst_amount':fields.float('GST amount', digits_compute=dp.get_precision('Account'),),
        'gst_amount_funct':fields.function(_get_gst_amount,type='float',string="GST Float", store={
            _name: (lambda self, cr,uid,ids,c: ids, ['amount'], 10),
            }),
        'appoint_detail_ids':fields.one2many('package.booking','contract_id','Appointment Detail'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(ref_no, company_id)', 'Order Reference must be unique per Company!'),
    ]

    _defaults = {
        'date_order': fields.date.context_today,
        'date_order2': fields.date.context_today,
        'state': 'draft',
        'period_id': _get_period,
        'invoice_exists': False,
        'expiring': False,
        'ref_no': _get_ref_no,
        'dk_subject': 'Breakdown of Air-conditioning equipment:',
        'has_schedule_date': True,
        'schedule_date_readonly':'-',
        'currency_id':_get_currency_id,
        'company_id': _get_default_company,
        'just_renew':False,
        'just_remind':False,
        'appoint_holder':_get_default_appoint_holder,
        'per_annum':'per annum',
        'gst_type2':_get_default_gst_type,
        'gst_amount_is':'GST amount is',
        'gst_type_select':'inclusive',
    }

dk_contract()

class remark_notice(osv.osv_memory):
    _name = 'remark.notice'

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(remark_notice, self).default_get(cr, uid, fields, context=context)
        contract_id = context.get('active_id')
        if isinstance(contract_id, list):
            purchase_order_id = contract_id[0]
        active_model = context.get('active_model')
        assert active_model in ('dk.contract'), 'Bad context propagation'
        if 'contract_id' in fields:
            res.update(contract_id=contract_id)
        return res

    def confirm(self, cr, uid, ids, context=None):
        for track in self.browse(cr,uid,ids):
            if track.contract_id:
                self.pool.get('dk.contract').write(cr,uid,track.contract_id.id,{'state':'invalid'})
                self.pool.get('dk.comment').create(cr,uid,{'remarks':track.remarks,
                                                           'contract_id':track.contract_id.id})
        return True

    _columns = {
        'remarks': fields.text('Remarks',required='True'),
        'contract_id':fields.many2one('dk.contract','Origin'),
    }
remark_notice()


class dk_comment(osv.osv):
    _name = 'dk.comment'

    _columns = {
        'remarks': fields.text('Remarks',required='True'),
        'contract_id':fields.many2one('dk.contract','Origin'),
    }
dk_comment()


class dk_last_svs_date(osv.osv):

    _name = 'dk.last_svs_date'
    _columns = {
        'remarks': fields.text('Remarks',),
        'contract_id':fields.many2one('dk.contract','Origin'),
        'last_svs_date':fields.date('Last Service Date'),
    }

dk_last_svs_date()


class dk_edit_history(osv.osv):

    _name = 'dk.edit_history'
    _columns = {
        'remarks': fields.text('Remarks',),
        'contract_id':fields.many2one('dk.contract','Origin'),
        'date':fields.datetime('Edited Date'),
        'user_id':fields.many2one('res.users','User'),
    }

dk_last_svs_date()


class dk_remark(osv.osv):
    _name = 'dk.remark'
    _columns = {
        'have_schedule':fields.boolean('Have Schedule'),
        'remarks': fields.text('Remarks'),
        'contract_id':fields.many2one('dk.contract','Origin'),
        'period_id':fields.many2one('account.period','Period'),
        'date':fields.date('Schedule Date'),
    }
    _defaults={
        'have_schedule':False,
    }

dk_comment()

