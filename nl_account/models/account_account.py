from odoo import models, fields, api, _
from datetime import date, timedelta


class AccountAccount(models.Model):
    _inherit = 'account.account'

    current_balance_in_currency = fields.Float(compute='_compute_current_balance_in_account_currency')
    closing_balance_in_currency = fields.Float(compute='_compute_closing_balance_in_account_currency')

    def get_balances(self, domain):
        self._cr.execute(f"""
            SELECT
                account_id AS account_id,
                SUM(amount_currency) AS amount_currency
            FROM
                account_move_line
            WHERE
                parent_state = 'posted'
                {domain}
            GROUP BY
                account_id
        """)
        result = {}
        for rec in self._cr.dictfetchall():
            result.update({rec.get('account_id'): rec.get('amount_currency')})
        return result

    
    def _compute_current_balance_in_account_currency(self):
        balances = self.get_balances(f"AND account_id IN ({','.join([str(i) for i in self.ids])})") 
        for record in self:
            record.current_balance_in_currency = balances.get(record.id, 0)

    def _compute_closing_balance_in_account_currency(self):
        domain = f"AND account_id IN ({','.join([str(i) for i in self.ids])}) AND date <= '{(date.today() - timedelta(1)).strftime('%Y-%m-%d')}'"
        balances = self.get_balances(domain)
        for record in self:
            record.closing_balance_in_currency = balances.get(record.id, 0)

    def action_account_statement_wizard(self):
        for rec in self:
            return {
                'name': _('Account Statement Report'),
                'res_model': 'account.statement.wizard',
                'view_mode': 'form',
                'context': {
                    'default_account_id': rec.id, 
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
