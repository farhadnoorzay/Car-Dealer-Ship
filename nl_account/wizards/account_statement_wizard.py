from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Wizard'
    _rec_name = 'journal_id'

    journal_id = fields.Many2one('account.journal')
    account_id = fields.Many2one('account.account')
    from_date = fields.Date(default=lambda self: date.today(), required=True)
    to_date = fields.Date(default=lambda self: date.today(), required=True)

    @api.constrains('journal_id', 'account_id')
    def _check_journal_and_account(self):
        for rec in self:
            if not rec.journal_id and not rec.account_id:
                raise ValidationError(_('Please specify either an account_id or journal_id.'))

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for rec in self:
            if rec.to_date < rec.from_date:
                raise ValidationError(_('Start date cannot be greater than end date.'))

    def action_print(self):
        for rec in self:
            data = {
                'ids': rec.journal_id.id if rec.journal_id else rec.account_id.id,
                'model': 'account.journal' if rec.journal_id else 'account.account',
                'form': rec.id,
            }
            return self.env.ref('nl_account.account_statement_report').report_action(self, data=data)
