from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from odoo.addons.nl_account.helpers import accounts

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    company_id = fields.Many2one(
        'res.company', 
        required=True, 
        default=lambda self: self.env.company
    )
    
    from_date = fields.Date(default=lambda self: date.today())
    to_date = fields.Date(default=lambda self: date.today())

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for rec in self:
            if rec.to_date < rec.from_date:
                raise ValidationError(_('Start date cannot be greater than end date.'))

    def get_partner_statement_data(self, from_date, to_date, partner_id, currency_id, company_id):
        data = []
        data += accounts.GET_PARTNER_ACCOUNT_ENTRIES(self, partner_id, currency_id, company_id, from_date, to_date)[0]
        opening_balance = accounts.GET_PARTNER_BALANCE(self, partner_id, currency_id,'<',from_date) or 0
        data.sort(key = lambda x: x.get('date'))

        if not data:
            raise ValidationError('No transaction found for the selected creteria.')

        return data,opening_balance
    
    def calculate_totals(self, report_data,opening_balance):
        total_credits = sum(rd.get('credit') for rd in report_data)
        total_debits = sum(rd.get('debit') for rd in report_data)
        balance= total_debits-total_credits
        closing_balance = opening_balance + total_debits-total_credits
        return total_credits, total_debits,balance, closing_balance
    
    def action_generate_pdf(self):
        report_data,opening_balance = self.get_partner_statement_data(self.from_date,self.to_date,self.partner_id,self.currency_id,self.company_id)
        total_credits, total_debits,balance,closing_balance = self.calculate_totals(report_data,opening_balance)
        
        for rec in self:
            data = {
                'wizard_id': rec.id,
                'partner_id': self.partner_id,
                'data':report_data,
                'opening_balance':opening_balance,
                'balance':balance,
                'total_credits':total_credits,
                'total_debits':total_debits,
                'closing_balance':closing_balance
                }
        report_action_id = self.env.ref('nl_account.customer_statement_report')
        report_action_id.name = f"Partner Statement-{self.partner_id.name}"
        return report_action_id.report_action(self, data=data)
        
    def action_generate_xls(self):
        report_data,opening_balance = self.get_partner_statement_data(self.from_date,self.to_date,self.partner_id,self.currency_id,self.company_id)
        total_credits, total_debits,balance,closing_balance = self.calculate_totals(report_data,opening_balance)
        
        for rec in self:
            data = {
                'wizard_id': rec.id,
                'partner_id': self.partner_id,
                'data':report_data,
                'opening_balance':opening_balance,
                'balance':balance,
                'total_credits':total_credits,
                'total_debits':total_debits,
                'closing_balance':closing_balance
                }
        report_action_id = self.env.ref('nl_account.customer_statement_report_xls')
        report_action_id.name = f"Partner Statement-{self.partner_id.name}"
        return report_action_id.report_action(self, data=data)
        