# -*- coding: utf-8 -*-

from report import report_sxw
import datetime

class payroll_summary_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(payroll_summary_report, self).__init__(cr, uid, name, context=context)
        self.result_emp = []
        self.result_emp1 = []
        self.final_group_total = []
        self.localcontext.update({
            'get_name': self.get_name,
            'datetime': datetime,
            'finalgrouptotal': self.finalgrouptotal,
            'get_groupname': self.get_groupname,
           })
    
    def get_groupname(self, date_from, date_to):
        start_date = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        month = start_date.strftime('%m')
        year = start_date.strftime('%Y')
        list = []
        res = {
               'period': month,
               'year': year,
            }
        list.append(res)
        return list
    
    def get_name(self, emp_ids, date_from, date_to):
        payslip_obj = self.pool.get('hr.payslip')
        hr_depart_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        result = {}
        total = {}
        employee_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', emp_ids)])
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            payslip_ids = payslip_obj.search(self.cr, self.uid, [('employee_id', '=', employee.id), ('date_from', '>=', date_from),
                                                                 ('date_from', '<=', date_to), ('state', 'in', ['draft', 'done', 'verify'])])
            commission = incentive = net = twage = lvd = exa = exd = gross = cpf = pf = overtime = backpay = bonus = donation = cpftotal = sdl = fwl = 0.0
            if not payslip_ids:
                continue
            for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                for rule in payslip.details_by_salary_rule_category:
                    if rule.code == 'SC102':
                        overtime += rule.total
                    if rule.code == 'SC104':
                        commission += rule.total
                    if rule.code == 'SC105':
                        incentive += rule.total
                    if rule.code == 'NET':
                        net += rule.total
                    if rule.code == 'SC206':
                        lvd += rule.total
                    if rule.code == 'SC122':
                        exa += rule.total
                    if rule.code == 'SC299':
                        exd += rule.total
                    if rule.code == 'GROSS':
                        gross += rule.total
                    if rule.category_id.code == 'CAT_CPF_EMPLOYEE':
                        cpf += rule.total
                    if rule.category_id.code == 'CAT_CPF_EMPLOYER':
                        pf += rule.total
                    if rule.category_id.code == 'CAT_CPF_TOTAL':
                        cpftotal += rule.total
                    if rule.code == 'SC48':
                        backpay += rule.total
                    if rule.code == 'SC121':
                        bonus += rule.total
                    if rule.register_id.name in ['CPF - ECF', 'CPF - MBMF', 'CPF - SINDA', 'CPF - CDAC']:
                        donation += rule.total
                    if rule.code == 'CPFSDL':
                        sdl += rule.total
                    if rule.code == 'CPFFWL':
                        fwl += rule.total
            payslip_result = {
                                'ename': payslip.employee_id.name or '',
                                'eid': payslip.employee_id and payslip.employee_id.user_id and payslip.employee_id.user_id.login or '',
                                'twage': payslip.contract_id.wage_to_pay,
                                'net': net,
                                'lvd': lvd,
                                'exa': exa,
                                'exd': exd,
                                'gross': gross,
                                'cpf': cpf,
                                'pf': pf,
                                'bonus': bonus,
                                'overtime': overtime,
                                'backpay': backpay,
                                'donation': donation,
                                'cpftotal': cpftotal,
                                'sdl': sdl,
                                'fwl': fwl,
                                'incentive': incentive,
                                'commission': commission
                        }
            if payslip.employee_id.department_id:
                if payslip.employee_id.department_id.id in result:
                    result.get(payslip.employee_id.department_id.id).append(payslip_result)
                else:
                    result.update({payslip.employee_id.department_id.id: [payslip_result]})
            else:
                if 'Undefine' in result:
                    result.get('Undefine').append(payslip_result)
                else:
                    result.update({'Undefine': [payslip_result]})
        finalcommission = finalincentive = finaltwage = finalnet = finallvd = finalexa = finalexd = finalgross = finalcpf = finalpf = finalovertime = finalbackpay = finalbonus = finaldonation = finalcpftotal = finalsdl = finalfwl = 0
        final_result = {}
        for key, val in result.items():
            if key == 'Undefine':
                category_name = 'Undefine'
            else:
                category_name = hr_depart_obj.browse(self.cr, self.uid, key).name
            total = {'name': category_name, 'commission': 0.0, 'incentive':0.0, 'twage': 0.0, 'net': 0.0, 'lvd': 0.0, 'exa': 0.0, 'exd': 0.0, 'gross':0.0, 'cpf': 0.0, 'pf': 0.0, 'overtime': 0.0, 'backpay': 0.0, 'bonus': 0.0, 'donation':0.0, 'cpftotal': 0.0, 'sdl': 0.0, 'fwl':0.0}
            for line in val:
                for field in line:
                    if field in total:
                        total.update({field:  total.get(field) + line.get(field)})
            final_result[key] = {'lines': val, 'total': total}
            finaltwage += total['twage']
            finalnet += total['net']
            finallvd += total['lvd']
            finalexa += total['exa']
            finalexd += total['exd']
            finalgross += total['gross']
            finalcpf += total['cpf']
            finalpf += total['pf']
            finalovertime += total['overtime']
            finalbackpay += total['backpay']
            finalbonus += total['bonus']
            finaldonation += total['donation']
            finalcpftotal += total['cpftotal']
            finalsdl += total['sdl']
            finalfwl += total['fwl']
            finalcommission += total['commission']
            finalincentive += total['incentive']
            
        final_total = {
                       'twage' : finaltwage,
                       'net' : finalnet,
                       'lvd' : finallvd,
                       'exa' : finalexa,
                       'exd' : finalexd,
                       'gross' : finalgross,
                       'cpf' : finalcpf,
                       'pf' : finalpf,
                       'overtime': finalovertime,
                       'backpay': finalbackpay,
                       'bonus': finalbonus,
                       'donation': finaldonation,
                       'cpftotal': finalcpftotal,
                       'sdl': finalsdl,
                       'fwl': finalfwl,
                       'commission': finalcommission,
                       'incentive': finalincentive
                }
        self.final_group_total.append(final_total)
        return final_result.values()

    def finalgrouptotal(self):
        return self.final_group_total

report_sxw.report_sxw('report.payrollsummary_receipt', 'hr.payslip', 'addons/payroll_extended/report/payroll_summary_report.rml', parser=payroll_summary_report)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

