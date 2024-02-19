from odoo import fields, models, api, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    confirmer_id = fields.Many2one('res.partner')
    payment_reference = fields.Char()
    activity_id = fields.Many2one('mail.activity')
    
    def action_post(self): 
        self.confirmer_id = self.env.user.partner_id.id
        self.activity_id.unlink()
        super(AccountPayment, self).action_post()

    def action_send_for_review(self):
        if self.state == 'draft':
            for user in self.env.ref('nl_account.group_finance_reviewer').users:
                self.activity_id = self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'account.payment')]).id,
                    'user_id': user.id,
                    'summary': 'Payment Approval',
                    'note': f'Payment Approval is waiting for your review.',
                    'activity_type_id': 4,
                    'date_deadline': date.today(),
                }).id
            self.write({'state': 'review'})
    
    def action_to_approve(self):
        for move in self:
            move.write({'state': 'to_approve'})

    def action_draft(self):
        self.activity_id.unlink()
        super().action_draft()
        