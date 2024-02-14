# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.addons.mail.models import mail_thread as MailThread

class ShipmentDetails(models.Model):
    _name = 'shipment.details'
    _description = 'Shipment Details'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _rec_name = 'reference'


    reference = fields.Char("Reference No", required=True, copy=False, readonly=True, default='New')  
    image = fields.Binary()
    shipment_date = fields.Date(string='Shipment Date', required=True, default=fields.Date.context_today)
    origin_port = fields.Char(string='Origin Port', required=True)
    destination_port = fields.Char(string='Destination Port', required=True)
    expected_arrival_date = fields.Date(string='Expected Arrival Date', required=True)
    tracking_number = fields.Char(string='Tracking Number', required=True)
    transportation_company = fields.Char(string='Transportation Company', required=True)
    vehicle_ids = fields.One2many('cds.vehicle', 'shipment_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
    ], string='State', default='draft', group_expand='_expand_states')
    

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('shipment.details.sequence')
        return super(ShipmentDetails, self).create(vals)
    
    
    def action_mark_draft(self):
        for record in self:
            record.state = 'draft'

    def action_mark_in_progress(self):
        for record in self:
            record.state = 'in_progress'

    def action_mark_completed(self):
        for record in self:
            record.state = 'completed'

    
    activity_ids = fields.One2many(
        'mail.activity',
        'res_id',
        domain=lambda self: [('res_model', '=', 'shipment.details')],
        string='Activities',
        auto_join=True,
        help="Activities related to this shipment",
    )

    message_follower_ids = fields.Many2many(
        'mail.followers',
        'shipment_followers_rel',  # Specify a different table name
        'res_id',
        'partner_id',
        string="Followers",
        copy=False,
    )


    message_ids = fields.One2many(
        'mail.message',
        'res_id',
        domain=lambda self: [('model', '=', 'shipment.details')],
        string='Messages',
        auto_join=True,
        help="Messages and communication history",
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]