# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveExtended(models.Model):
    _inherit = 'account.move'
    
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('to_approve', 'To Approve'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    internal_transfer_id = fields.Many2one(
        'internal.transfer'
    )
    
    usd_currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id)
    total_amount_in_usd = fields.Monetary(compute="_compute_total_amount_in_usd", currency_field='usd_currency_id')
    is_reviewer = fields.Boolean(compute="_compute_reviewers")
    is_approver = fields.Boolean(compute="_compute_reviewers")

    def _compute_reviewers(self):
        for rec in self:
            rec.is_reviewer = self.env.user == self.env.company.accounting_reviewer_id
            rec.is_approver = self.env.user == self.env.company.accounting_approver_id


    @api.depends('line_ids')
    def _compute_total_amount_in_usd(self):
        for rec in self:
            rec.total_amount_in_usd = False
            if rec.line_ids:
                total_debit = sum([line.debit for line in rec.line_ids])
                rec.total_amount_in_usd = self.env.company.currency_id._convert(
                                total_debit, rec.usd_currency_id, rec.company_id, rec.date or fields.Date.today())
    

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [
                # ('type', '=', journal_type),
                ('company_id', '=', company_id)
            ]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    def action_review(self):
        for move in self:
            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                elif move.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))
                
            if not move.line_ids.filtered(lambda line: line.display_type not in ('line_section', 'line_note')):
                raise UserError(_('You need to add a line before submitting for review.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))
            move.write({'state': 'review'})
            move._create_activity(self.env.company.accounting_reviewer_id)

    
    def action_to_approve(self):
        for move in self:
            move.write({'state': 'to_approve'})
            move._get_user_accounting_entry_activities(self.env.company.accounting_reviewer_id).action_feedback()
            move._create_activity(self.env.company.accounting_approver_id)

    def action_post(self):
        res = super(AccountMoveExtended, self).action_post()
        self._get_user_accounting_entry_activities(self.env.company.accounting_approver_id).action_feedback()
        return res
            

    def open_internal_transfer(self):
        for rec in self:
            rec.ensure_one()
            action = rec.env['ir.actions.act_window']._for_xml_id(
                'nl_account.action_internal_transfer_window')
            form = rec.env.ref('nl_account.internal_transfer_view_form', False)
            form_view = [(form.id if form else False, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

            action['res_id'] = rec.internal_transfer_id.id
            return action
        

    def _create_activity(self, approver):
        for rec in self:
            rec.activity_schedule(
                'nl_account.mail_activity_accounting_entry',
                user_id=approver.id,
                note=f'Please approve accounting entry ({rec.name})')
            
    def _get_user_accounting_entry_activities(self, user):
        domain = [
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', self.env.ref('nl_account.mail_activity_accounting_entry').id),
            ('user_id', '=', user.id)
        ]
        return self.env['mail.activity'].search(domain)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    internal_transfer_1st = fields.Many2one('internal.transfer')
    internal_transfer_2st = fields.Many2one('internal.transfer')    