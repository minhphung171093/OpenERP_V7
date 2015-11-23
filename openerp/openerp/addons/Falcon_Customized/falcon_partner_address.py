# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class falcon_partner_address(osv.osv):
    _name = 'falcon.partner.address'
    _order = 'type, name'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other') ],'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
        'function': fields.char('Function', size=64),
        'title': fields.many2one('res.partner.title','Title'),
        'name': fields.char('Contact Name', size=64, select=1),
        'street': fields.char('Line 1', size=128),
        'street2': fields.char('Line 2', size=128),
        'street3': fields.char('Line 3', size=128),
        'street4': fields.char('Line 4', size=128),
        'zip': fields.char('Postcode', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'Fed. State', domain="[('country_id','=',country_id)]"),
        'state_name': fields.char('State',size=25),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('E-Mail', size=240),
        'phone': fields.char('Phone 1', size=64),
        'phone2': fields.char('Phone 2', size=64),
        'phone3': fields.char('Phone 3', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
        'birthdate': fields.char('Birthdate', size=64),
        'is_customer_add': fields.related('partner_id', 'customer', type='boolean', string='Customer'),
        'is_supplier_add': fields.related('partner_id', 'supplier', type='boolean', string='Supplier'),
         'website': fields.char('Website', size=128, select=1),
    }

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                addr = r['name'] or ''
                if r['name'] and (r['city'] or r['country_id']):
                    addr += ', '
                addr += (r['country_id'] and r['country_id'][1] or '') + ' ' + (r['city'] or '') + ' '  + (r['street'] or '')
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr.strip() or '/')))
                else:
                    res.append((r['id'], addr.strip() or '/'))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if context.get('contact_display', 'contact')=='partner ' or context.get('contact_display', 'contact')=='partner_address '  :
            ids = self.search(cr, user, [('partner_id',operator,name)], limit=limit, context=context)
        else:
            if not name:
                ids = self.search(cr, user, args, limit=limit, context=context)
            else:
                ids = self.search(cr, user, [('zip','=',name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('city',operator,name)] + args, limit=limit, context=context)
            if name:
                ids += self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
                ids += self.search(cr, user, [('partner_id',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    def get_city(self, cr, uid, id):
        return self.browse(cr, uid, id).city
falcon_partner_address()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

