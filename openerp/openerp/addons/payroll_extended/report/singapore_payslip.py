#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
from operator import itemgetter
import datetime

class singapore_payslip(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(singapore_payslip, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_details_by_rule_category': self.get_details_by_rule_category,
            'get_lines_by_contribution_register': self.get_lines_by_contribution_register,
            'get_contract_day': self.get_contract_day,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to
        })

    def get_date_from(self, date_from):
        date_from = datetime.datetime.strptime(date_from , '%Y-%m-%d').strftime("%d-%B-%Y")
        return str(date_from)

    def get_date_to(self, date_to):
        date_to = datetime.datetime.strptime(date_to , '%Y-%m-%d').strftime("%d-%B-%Y")
        return str(date_to)

    def get_contract_day(self, payslip_id):
        payslip_obj = self.pool.get('hr.payslip')
        contract_days = 0
        for payslip in payslip_obj.browse(self.cr, self.uid, [payslip_id]):
            for work in payslip.worked_days_line_ids:
                if work.code == 'TTLCURCONTDAY':
                    contract_days = work.number_of_days
        return int(contract_days)

    def get_details_by_rule_category(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        rule_cate_obj = self.pool.get('hr.salary.rule.category')

        def get_recursive_parent(rule_categories):
            if not rule_categories:
                return []
            if rule_categories[0].parent_id:
                rule_categories.insert(0, rule_categories[0].parent_id)
                get_recursive_parent(rule_categories)
            return rule_categories

        res = []
        result = {}
        ids = []
        res1=[]

        for id in range(len(obj)):
            ids.append(obj[id].id)
        if ids:
            self.cr.execute('''SELECT pl.id, pl.category_id FROM hr_payslip_line as pl \
                LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id) \
                WHERE pl.id in %s \
                GROUP BY rc.parent_id, pl.sequence, pl.id, pl.category_id \
                ORDER BY pl.sequence, rc.parent_id''',(tuple(ids),))
            for x in self.cr.fetchall():
                result.setdefault(x[1], [])
                result[x[1]].append(x[0])
            for key, value in result.iteritems():
                rule_categories = rule_cate_obj.browse(self.cr, self.uid, [key])
                parents = get_recursive_parent(rule_categories)
                category_total = 0
                for line in payslip_line.browse(self.cr, self.uid, value):
                    category_total += line.total
                level = 0
                for parent in parents:
                    if parent.code == 'BASIC':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 1
                        })
                        level += 1
                    if parent.code == 'ALW':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 2
                        })
                        level += 1
                    if parent.code == 'ADD':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 3
                        })
                        level += 1
                    if parent.code == 'GROSS':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 4
                        })
                        level += 1
                    if parent.code == 'DED':
                        res.append({
                            'rule_category': 'Less : ' + parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 5
                        })
                        level += 1
                    if parent.code == 'CAT_CPF_EMPLOYEE':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 6
                        })
                        level += 1
                    if parent.code == 'CATCPFAGENCYSERVICESEE':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 7
                        })
                        level += 1
                    if parent.code == 'CATCPFFWL':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 8
                        })
                        level += 1
                    if parent.code == 'CATCPFSDL':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 9
                        })
                        level += 1
                    if parent.code == 'CAT_CPF_TOTAL':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 10
                        })
                        level += 1
                    if parent.code == 'NET':
                        res.append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': category_total,
                            'sequence': 11
                        })
                        level += 1
                
                
                for line in payslip_line.browse(self.cr, self.uid, value):
                    if line.category_id.code == 'BASIC':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 1
                        })
                    if line.category_id.code == 'ALW':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 2
                        })
                    if line.category_id.code == 'ADD':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 3
                        })
                    if line.category_id.code == 'GROSS':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 4
                        })
                    if line.category_id.code == 'DED':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 5
                        })
                    if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 6
                        })
                    if line.category_id.code == 'CATCPFAGENCYSERVICESEE':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 7
                        })
                    if line.category_id.code == 'CATCPFFWL':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 8
                        })
                    if line.category_id.code == 'CATCPFSDL':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 9
                        })
                    if line.category_id.code == 'CAT_CPF_TOTAL':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 10
                        })
                    if line.category_id.code == 'NET':
                        res.append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level,
                            'sequence': 11
                        })
        res = sorted(res, key=itemgetter('sequence'))
        return res

    def get_lines_by_contribution_register(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        result = {}
        res = []

        for id in range(len(obj)):
            if obj[id].register_id:
                result.setdefault(obj[id].register_id.name, [])
                result[obj[id].register_id.name].append(obj[id].id)
        for key, value in result.iteritems():
            register_total = 0
            for line in payslip_line.browse(self.cr, self.uid, value):
                register_total += line.total
            res.append({
                'register_name': key,
                'total': register_total,
            })
            for line in payslip_line.browse(self.cr, self.uid, value):
                res.append({
                    'name': line.name,
                    'code': line.code,
                    'quantity': line.quantity,
                    'amount': line.amount,
                    'total': line.total,
                })
        return res

report_sxw.report_sxw('report.singaporepayslip', 'hr.payslip', 'payroll_extended/report/report_payslip_details.rml', parser=singapore_payslip, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

