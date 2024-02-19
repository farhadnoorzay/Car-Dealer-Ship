from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from odoo.addons.nl_account.helpers import accounts

class CustomerBalanceWizard(models.TransientModel):
    _name = 'customer.balance.wizard'
    _description = 'Customer Balance Wizard'
    
    name = fields.Char(
        string='Name',
    )
    currency_ids = fields.Many2many(
        string='Currencies',
        comodel_name='res.currency',
        relation='res_currency_customer_balance_wizard_rel',
        column1='currency_id',
        column2='wizard_id',
        required=True
    )
    date = fields.Date(default=lambda self: date.today(),string="Balance as of",required=True)

    def get_partner_balance_data(self):
        
        partner_ids = self.env['res.partner'].search([])
        data = {}

        for partner_id in partner_ids:
            data[partner_id.id] = {'partner_name':(partner_id.sequence or '') + '|' + (partner_id.name or '')}

            for currency_id in self.currency_ids:
                partner_balance = accounts.GET_PARTNER_BALANCE(self, partner_id, currency_id, '<=',self.date) or 0
                data[partner_id.id][currency_id.name] = partner_balance

        report_data = {partner: balances for partner, balances in data.items() if any(balance != 0 for balance in balances.values())}
        if not report_data:
            raise ValidationError('No transaction found for the selected criteria')

        return report_data

    def action_generate_pdf(self):
        report_data = self.get_partner_balance_data()
        data = {
            'date': self.date,
            'report_data':report_data,
            'wizard_id': self.id}
        
        report_action_id = self.env.ref('nl_account.customer_balance_report')
        report_action_id.name = f"Partners Balance"
        return report_action_id.report_action(self, data=data)
        
    def action_generate_xls(self):
        report_data = self.get_partner_balance_data()
        data = {
            'date': self.date,
            'report_data':report_data,
            'wizard_id': self.id}
        
        report_action_id = self.env.ref('nl_account.customer_balance_report_xls')
        report_action_id.name = f"Partners Balance"
        return report_action_id.report_action(self, data=data) 
