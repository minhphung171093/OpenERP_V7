# -*- coding: utf-8 -*-


from openerp.osv import fields, osv
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools.translate import _
from operator import itemgetter

class account_aged_trial_balance(osv.osv_memory):
    _inherit = "account.aged.trial.balance"
    _name = 'account.aged.trial.balance'
    _description = 'TGB Trial Balance Report'

    def _get_default_partners(self, cr, uid, context=None):
        if context.get('active_model') and context['active_model'] == 'res.partner':
            return self.pool.get('res.partner').search(cr, uid, [('id', 'in', context['active_ids'])], context=context)
        return False

    _columns = {
                'partners': fields.many2many('res.partner', 'custom_report_aged_partner_rel', 'partners', 'partner_id', 'Partners', required=False),
    }

    _defaults = {
        'partners': _get_default_partners,
    }

    def _move_ids(self, cr, uid, ids, context=None):
        """
        @return: dictionary whose keys are partner ids, and values are lists
        of move line ids relevant to the partner and wizard input
        """
        move_line_pool = self.pool.get('account.move.line')
        fields = self.read(cr,uid,ids,['partners', 'target_move', 'result_selection', 'company_id',], context=context)[0]

        move_state = ['draft','posted']
        if fields['target_move'] == 'posted':
            move_state = ['posted']
        search_tuples = [('move_id.state', 'in', move_state)]

        partner_ids = fields['partners']
        search_tuples.append(('partner_id', 'in', partner_ids))
        if fields['result_selection'] == 'customer_supplier':
            search_tuples.append(('account_id.type', 'in', ['receivable', 'payable']))
        else:
            search_tuples.append(('account_id.type', '=', fields['result_selection']))

        company_ids = [fields['company_id'][0]]
        search_tuples.append(('company_id', 'in', company_ids))
        ids = move_line_pool.search(cr, uid, search_tuples)
        ids.reverse()
        move_lines = move_line_pool.browse(cr, uid, ids, context)
        res = dict((partner_id, []) for partner_id in partner_ids)
        for line in move_lines:
            if line.partner_id.id in partner_ids:
                res[line.partner_id.id].append(line.id)
        return res

    def _get_partners(self, cr, uid, ids, context=None):
        """
        @param move_ids: a dictionary with key partner_id, and a list of move_ids
        @return: a list of ints (partner_ids) ordered alphabetically
        """

        partner_obj = self.pool.get('res.partner')
        fields = self.read(cr, uid, ids, ['partners', 'result_selection'], context=context)[0]
        partner_ids = fields['partners']
        res_partners = partner_obj.browse(cr, uid, partner_ids, context)
        if fields['result_selection'] == 'receivable':
            partner_ids = [partner.id for partner in res_partners if partner.customer]
        elif fields['result_selection'] == 'payable':
            partner_ids = [partner.id for partner in res_partners if partner.supplier]
        elif fields['result_selection'] == 'customer_supplier':
            partner_ids = [partner.id for partner in res_partners]
        partner_ids = [x['id'] for x in sorted(partner_obj.read(cr, uid, partner_ids, ['id', 'name']), key=itemgetter('name'))]
        return partner_ids



    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['partner_ids'] = self._get_partners(cr, uid, ids, context)
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._tgb_print_report(cr, uid, ids, data, context=context)

    def _tgb_print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.tgb_aged_trial_balance',
            'datas': data
        }

account_aged_trial_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
