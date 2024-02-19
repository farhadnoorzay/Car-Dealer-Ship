from odoo import models, _
from odoo.exceptions import ValidationError
# from odoo.addons.nl_account.helpers import accounts

class AccountStatementReport(models.AbstractModel):
    _name = 'report.nl_account.account_statement_report_template'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('nl_account.account_statement_report')
        wizard_id = self.env['account.statement.wizard'].browse(data.get('form'))
        journal_id = wizard_id.journal_id
        account_id = wizard_id.account_id if wizard_id.account_id else journal_id.default_account_id

        if not account_id:
            raise ValidationError(_('The chosen journal does not have a default account.'))
        
        if not account_id.currency_id:
            raise ValidationError(_('The account does not have currency.'))

        # Lines
        self._cr.execute("""
            SELECT
                move.name AS name,
                move.date::TEXT AS move_date,
                line.name AS label,
                line.debit AS debit,
                line.credit AS credit,
                line.amount_currency AS amount_currency,
                partner.name AS partner_name
            FROM
                account_move AS move
            INNER JOIN
                account_move_line AS line ON line.move_id = move.id
            LEFT JOIN
                res_partner AS partner ON line.partner_id = partner.id
            WHERE
                move.state = 'posted'
            AND
                (move.date BETWEEN %s AND %s)
            AND
                line.account_id = %s
            ORDER BY
                move.date ASC, move.id ASC
            """, (wizard_id.from_date, wizard_id.to_date, account_id.id))

        data = self._cr.dictfetchall()
        if not data:
            raise ValidationError(_('No records found for the chosen journal and period.'))
        # Opening Balance
        self._cr.execute("""
            SELECT
                COALESCE(SUM(line.debit) - SUM(line.credit), 0) AS balance,
                COALESCE(SUM(line.amount_currency), 0) AS balance_currency
            FROM
                account_move_line AS line
            INNER JOIN
                account_move AS move ON move.id = line.move_id
            WHERE
                move.state = 'posted'
            AND
                move.date < %s
            AND
                line.account_id = %s LIMIT 1
            """, (wizard_id.from_date, account_id.id))
        account_balance = self._cr.dictfetchone()
        return {
            'docs': wizard_id,
            'doc_ids': data,
            'doc_model': report.model,
            'account_balance': account_balance,
            'account_id': account_id,
            'journal_id': journal_id
        }