# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    # def onchange_company_address(self,cr,uid,ids,parent_id,use_company_address):
    #     val = {}
    #     if use_company_address is True:
    #         company_id = self.pool.get('res.partner').browse(cr,uid,parent_id)
    #         val['street']= company_id.street
    #         val['street2']= company_id.street2
    #         val['city']= company_id.city
    #         val['state_id']= company_id.state_id.id
    #         val['zip']= company_id.zip
    #         val['country_id']= company_id.country_id.id
    #         val['phone']= company_id.phone
    #         val['mobile']= company_id.mobile
    #         val['fax']= company_id.fax
    #     return {'value':val}


    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        def value_or_id(val):
            """ return val or val.id if val is a browse record """
            return val if isinstance(val, (bool, int, long, float, basestring)) else val.id
        result = {}
        if parent_id:
            if ids:
                partner = self.browse(cr, uid, ids[0], context=context)
                if partner.parent_id and partner.parent_id.id != parent_id:
                    result['warning'] = {'title': _('Warning'),
                                         'message': _('Changing the company of a contact should only be done if it '
                                                      'was never correctly set. If an existing contact starts working for a new '
                                                      'company then a new contact should be created under that new '
                                                      'company. You can use the "Discard" button to abandon this change.')}
            parent = self.browse(cr, uid, parent_id, context=context)
            address_fields = self._address_fields(cr, uid, context=context)
            result['value'] = dict((key, value_or_id(parent[key])) for key in address_fields)
            result['value']['phone']= parent.phone
            result['value']['mobile']= parent.mobile
            result['value']['fax']= parent.fax
        else:
            result['value'] = {'use_parent_address': False}
        return result


    _columns = {
        'use_company_address': fields.boolean('Use company Address'),
    }
res_partner()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

