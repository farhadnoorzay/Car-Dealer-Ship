# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class InternalTransfer(models.Model):
    _name = 'internal.transfer'
    _description = 'Internal Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'
    _order = 'create_date desc'

    reference = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: _('New')
    )
    internal_reference = fields.Char(
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    date = fields.Date(
        default=fields.Date.context_today,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )
    origin_id = fields.Many2one(
        'account.journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    origin_current_balance = fields.Monetary(
        currency_field='currency_id',
        string='Current Balance',
        compute='_compute_current_origin_balance',
        store=True,
    )
    destination_id = fields.Many2one(
        'account.journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    destination_current_balance = fields.Monetary(
        currency_field='destination_currency',
        string='Current Balance',
        compute='_compute_current_destination_balance',
        store=True,
    )
    amount = fields.Monetary(
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount_in_words = fields.Char(
        compute='_compute_amount_to_word', store=True
    )
    currency_id = fields.Many2one(
        'res.currency', related='origin_id.default_account_id.currency_id')
    destination_currency = fields.Many2one(
        'res.currency', related='destination_id.default_account_id.currency_id')
    amount_in_destination_currency = fields.Monetary(
        'Amount in Destination',
        readonly=True,
        currency_field='destination_currency',
        states={'draft': [('readonly', False)]}
    )
    destination_amount_in_words = fields.Char(
        'Amount In Words',
        compute='_compute_destination_amount_to_word', store=True
    )

    amount_in_base_currency = fields.Float(
        compute="_compute_amount_in_base_currency"
    )

    memo = fields.Char(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('complete', 'Completed'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')
    ], default="draft", tracking=True
    )
    journal_entry_id = fields.Many2one(
        'account.move'
    )
    bank_fee_journal_entry_id = fields.Many2one(
        'account.move'
    )
    jouranl_item_ids = fields.One2many(
        'account.move.line', 'internal_transfer_1st', related='journal_entry_id.line_ids')
    fee_account_id = fields.Many2one(
        'account.account'
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
    )
    fee_amount = fields.Monetary(
        currency_field='fee_currency_id',
    )
    fee_currency_id = fields.Many2one('res.currency')
    reviewed_by_id = fields.Many2one('res.users')

    @api.model
    def create(self, vals):
        result = super(InternalTransfer, self).create(vals)
        result['reference'] = "INTERNAL" + self.env['ir.sequence'].next_by_code(
            'generate.internal.transfer.sequence') or _('New')
        return result

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    'Items can only be deleted in the draft state.')
            record_ids = rec.ids
            result = super(InternalTransfer, self).unlink()
            rec.env['mail.activity'].sudo().search(
                [('res_model', '=', rec._name), ('res_id', 'in', record_ids)]
            ).unlink()
            return result

    @api.onchange('amount', 'origin_id', 'destination_id')
    def _change_amount_in_destination_currency(self):
        for rec in self:
            rec.amount_in_destination_currency = False
            if rec.origin_id and rec.destination_id:
                rec.amount_in_destination_currency = rec.origin_id.default_account_id.currency_id._convert(
                    rec.amount, rec.destination_id.default_account_id.currency_id, rec.company_id, rec.date)

    @api.depends('amount', 'origin_id')
    def _compute_amount_in_base_currency(self):
        for rec in self:
            rec.amount_in_base_currency = False
            if rec.origin_id:
                rec.amount_in_base_currency = rec.origin_id.default_account_id.currency_id._convert(
                    rec.amount, rec.company_id.currency_id, rec.company_id, rec.date)

    @api.depends('amount', 'currency_id')
    def _compute_amount_to_word(self):
        for rec in self:
            rec.amount_in_words = False
            if rec.currency_id:
                rec.amount_in_words = rec.currency_id.amount_to_text(rec.amount)

    @api.depends('amount_in_destination_currency', 'destination_currency')
    def _compute_destination_amount_to_word(self):
        for rec in self:
            rec.destination_amount_in_words = False
            if rec.destination_currency:
                rec.destination_amount_in_words = rec.destination_currency.amount_to_text(
                    rec.amount_in_destination_currency)
            
    

    @api.depends('origin_id')
    def _compute_current_origin_balance(self):
        for rec in self:
            rec.origin_current_balance = rec.origin_id.default_account_id.current_balance_in_currency

    @api.depends('destination_id')
    def _compute_current_destination_balance(self):
        for rec in self:
            rec.destination_current_balance = rec.destination_id.default_account_id.current_balance_in_currency

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_('Transfer amount must be greater than 0.'))

    @api.onchange('origin_id')
    def _onchange_origin(self):
        if self.origin_id and not self.origin_id.default_account_id.currency_id:
            raise ValidationError(
                _("Set currency for the journal's default account."))

    @api.onchange('destination_id')
    def _onchange_destination(self):
        if self.destination_id and not self.destination_id.default_account_id.currency_id:
            raise ValidationError(
                _("Set currency for the journal's default account."))

    # Header Action

    def action_submit_review(self):
        for rec in self:
            return {
                'name': _('Bank Fee'),
                'res_model': 'internal.transfer.fee.wizard',
                'view_mode': 'form',
                'context': {
                    'default_currency_id': rec.currency_id.id,
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

    def action_complete(self):
        for rec in self:
            if not rec.env.user.has_group('account.group_account_manager') or rec.state != 'under_review':
                return

            rec.action_create_journal_entry(
                debit_amount=rec.amount_in_base_currency,
                credit_amount=rec.amount_in_base_currency,
                currency_debit_amount=rec.amount_in_destination_currency,
                currency_credit_amount=rec.amount,
                credit_account_id=rec.origin_id.default_account_id,
                debit_account_id=rec.destination_id.default_account_id,
            )
            rec.write({
                'state': 'complete',
                'reviewed_by_id': rec.env.user.id
            })
            for user in rec.env.ref('account.group_account_manager').users.ids:
                rec._get_activities(user).action_feedback()

    def action_draft(self):
        for rec in self:
            if not rec.env.user.has_group('account.group_account_manager'):
                return
            rec.write({'state': 'draft'})
            if rec.journal_entry_id:
                rec.journal_entry_id.sudo().button_draft()
                rec.journal_entry_id.sudo().with_context(force_delete=True).unlink()

            if rec.bank_fee_journal_entry_id:
                rec.bank_fee_journal_entry_id.sudo().button_draft()
                rec.bank_fee_journal_entry_id.sudo().with_context(force_delete=True).unlink()

            rec.fee_amount = False
            rec.fee_currency_id = False

    def action_cancel(self):
        for rec in self:
            if not rec.env.user.has_group('account.group_account_manager'):
                return
            rec.write({'state': 'cancel'})
            for user in rec.env.ref('account.group_account_manager').users.ids:
                rec._get_activities(user).action_feedback()

    def action_reject(self):
        for rec in self:
            if not rec.env.user.has_group('account.group_account_manager'):
                return
            rec.write({'state': 'reject'})
            for user in rec.env.ref('account.group_account_manager').users.ids:
                rec._get_activities(user).action_feedback()

    # Smart Button actions
    def open_journal_entries(self):
        for rec in self:
            rec.ensure_one()
            action = rec.env['ir.actions.act_window']._for_xml_id(
                'account.action_move_journal_line')
            form = rec.env.ref('account.view_move_form', False)
            form_view = [(form.id if form else False, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

            action['res_id'] = rec.bank_fee_journal_entry_id.id if rec.env.context.get(
                'fee') else rec.journal_entry_id.id
            return action

    # Helpers
    def action_create_journal_entry(self,
                                    debit_amount,
                                    credit_amount,
                                    currency_debit_amount,
                                    currency_credit_amount,
                                    credit_account_id,
                                    debit_account_id,
                                    ):
        for rec in self:
            if not rec.env.company.internal_transfer_default_journal:
                raise ValidationError(_('There is no journal set for Internal Transfer. Kindly contact the Administrator.'))
            line_ids = [
                # debit line
                {
                    'account_id': debit_account_id.id,
                    'debit': debit_amount,
                    'credit': 0,
                    'amount_currency': currency_debit_amount,
                    'name': rec.memo,
                    'currency_id': debit_account_id.currency_id.id,
                },
                # Credit Line
                {
                    'account_id': credit_account_id.id,
                    'debit': 0,
                    'credit': credit_amount,
                    'amount_currency': -(currency_credit_amount),
                    'name': rec.memo,
                    'currency_id': credit_account_id.currency_id.id,
                }
            ]
            move = rec.env['account.move'].sudo().create({
                'ref': rec.internal_reference,
                'line_ids': [(0, 0, line_vals) for line_vals in line_ids],
                'journal_id': rec.env.company.internal_transfer_default_journal.id,
                'internal_transfer_id': rec.id,
                'date': rec.date,

            })
            move.sudo().action_post()
            rec.journal_entry_id = move.id

            if rec.fee_amount > 0:
                fee_line_ids = [
                    # debit Line (Bank fee)
                    {
                        'account_id': rec.fee_account_id.id,
                        'debit': rec.fee_currency_id._convert(rec.fee_amount, rec.company_id.currency_id, rec.company_id, rec.date),
                        'credit': 0,
                        'amount_currency': rec.fee_amount,
                        'name': rec.memo,
                        'currency_id': rec.fee_currency_id.id,
                    },
                    # Credit Line (Bank fee)
                    {
                        'account_id': rec.journal_id.default_account_id.id,
                        'debit': 0,
                        'credit': rec.fee_currency_id._convert(rec.fee_amount, rec.company_id.currency_id, rec.company_id, rec.date),
                        'amount_currency': -(rec.fee_amount),
                        'name': rec.memo,
                        'currency_id': rec.fee_currency_id.id,
                    }
                ]
                bank_fee_move = rec.env['account.move'].sudo().create({
                    'ref': rec.internal_reference,
                    'line_ids': [(0, 0, vals) for vals in fee_line_ids],
                    'journal_id': rec.env.company.internal_transfer_default_journal.id,
                    'internal_transfer_id': rec.id,
                    'date': rec.date,

                })
                bank_fee_move.sudo().action_post()
                rec.bank_fee_journal_entry_id = bank_fee_move.id

    def _create_activity(self):
        for rec in self:
            for user in rec.env.ref('nl_account.group_finance_reviewer').users.ids:
                rec.activity_schedule(
                    'nl_account.mail_activity_internal_transfer_review',
                    user_id=user,
                    note=f'Please review internal transfer ({rec.reference}).')

    def _get_activities(self, user):
        domain = [
            ('res_model', '=', 'internal.transfer'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', self.env.ref(
                'nl_account.mail_activity_internal_transfer_review').id),
            ('user_id', '=', user)
        ]
        return self.env['mail.activity'].search(domain)
