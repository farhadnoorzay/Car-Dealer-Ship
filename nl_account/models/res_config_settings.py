# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_account_afn_domain(self):
        currency = self.env.ref('base.AFN')
        return [('internal_group', '=', 'asset'), ('account_type', '=', 'asset_prepayments'), ('company_id', '=', self.env.company.id), ('currency_id', '=', currency.id)]
    
    def _get_account_usd_domain(self):
        currency = self.env.ref('base.USD')
        return [('internal_group', '=', 'asset'), ('account_type', '=', 'asset_prepayments'), ('company_id', '=', self.env.company.id), ('currency_id', '=', currency.id)]
    # Account
    internal_transfer_fee_account_id = fields.Many2one(
        comodel_name='account.account', 
        string='Bank Fee Account', 
        domain ="[('internal_group', '=', 'expense'), ('account_type', '=', 'expense'), ('company_id', '=', company_id)]",
        )
 
    internal_transfer_default_journal = fields.Many2one(
        comodel_name='account.journal',
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]"
    )


    accounting_reviewer_id = fields.Many2one('res.users')
    accounting_approver_id = fields.Many2one('res.users')

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    # Account
    internal_transfer_fee_account_id = fields.Many2one(
        string='Bank Fee Account', 
        related='company_id.internal_transfer_fee_account_id',
        readonly=False
        )
    internal_transfer_default_journal = fields.Many2one(
        related='company_id.internal_transfer_default_journal',
        readonly=False
    )

    accounting_reviewer_id = fields.Many2one(related='company_id.accounting_reviewer_id', readonly=False, domain=lambda self: [('groups_id', '=', self.env.ref('account.group_account_manager').id)])
    accounting_approver_id = fields.Many2one(related='company_id.accounting_approver_id', readonly=False, domain=lambda self: [('groups_id', '=', self.env.ref('account.group_account_manager').id)])