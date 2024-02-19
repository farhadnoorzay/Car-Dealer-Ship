# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.addons.mail.models import mail_thread as MailThread
from odoo.exceptions import ValidationError

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
            for vehicle in record.vehicle_ids:
                vehicle.action_mark_dock()
            record.state = 'completed'
    


    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
    

    # @api.constrains('state')
    # def _check_add_vehicle_to_completed_shipment(self):
    #     for shipment in self:
    #         if shipment.state == 'completed' and shipment.vehicle_ids:
    #             raise ValidationError("Cannot add more vehicles to a completed shipment.")