# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class InternalTransferFee(models.TransientModel):
    _name = 'internal.transfer.fee.wizard'
    _description = 'Internal Transfer Fee'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    fee_account_id = fields.Many2one(
        'account.account',
        default=lambda self: self.env.company.internal_transfer_fee_account_id,
        domain="[('internal_group', '=', 'expense'), ('account_type', '=', 'expense'), ('company_id', '=', company_id)]",
    )
    fee_amount = fields.Monetary()
    internal_transfer_id = fields.Many2one('internal.transfer',
                                           default=lambda self: self.env.context.get(
                                               'active_id')
                                           )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain="[('company_id', '=', company_id), ('currency_id', '=', currency_id), ('type', 'in', ('bank', 'cash'))]",
    )
    currency_id = fields.Many2one(
        'res.currency', readonly=False)

    has_fee = fields.Boolean(compute='_compute_has_fee')

    @api.depends('fee_amount')
    def _compute_has_fee(self):
        for rec in self:
            rec.has_fee = True if rec.fee_amount > 0 else False

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        self.journal_id = False

    def actoin_submit_transfer(self):
        vals = {'state': 'under_review'}
        if self.has_fee:
            vals.update({
                'fee_account_id': self.fee_account_id.id,
                'fee_amount': self.fee_amount,
                'journal_id': self.journal_id.id,
                'fee_currency_id': self.currency_id.id,
            })
        self.internal_transfer_id.write(vals)
        self.internal_transfer_id._create_activity()
