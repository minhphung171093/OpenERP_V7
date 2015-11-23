# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, expression

class account_period(osv.osv):
    _inherit = "account.period"


    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        search_name = ''
        if len(name) == 2:
            search_name='20'+name
        if len(name)==4:
            search_name=name[2:4]+'/20'+name[0:2]
            print 'search', search_name
        return super(account_period,self).name_search(cr,user,search_name,args,operator,context,limit)


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['code','name'], context=context)
        res = []
        for record in reads:
            period = record['code'].split('/')
            mon = period[0]
            name=record['name']
            if period[0]=='01':
                mon="JAN'"
            elif period[0]=='02':
                mon="FEB'"
            elif period[0]=='03':
                mon="MAR'"
            elif period[0]=='04':
                mon="APR'"
            elif period[0]=='05':
                mon="MAY'"
            elif period[0]=='06':
                mon="JUN'"
            elif period[0]=='07':
                mon="JUL'"
            elif period[0]=='08':
                mon="AUG'"
            elif period[0]=='09':
                mon="SEP'"
            elif period[0]=='10':
                mon="OCT'"
            elif period[0]=='11':
                mon="NOV'"
            elif period[0]=='12':
                mon="DEC'"
            else:
                mon=record['name']
            if mon!=record['name']:
                name = mon+period[1][-2:]
            # name = mon+period[1][-2:]
            res.append((record['id'], name))
        return res

account_period()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
