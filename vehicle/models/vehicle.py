# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.addons.mail.models import mail_thread as MailThread
from odoo.exceptions import ValidationError







year_range = [(str(year), str(year)) for year in range(1990, 2029)]

class Vehicle(models.Model):
    _name = 'cds.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    shipment_details_ids = fields.One2many('shipment.details', 'vehicle_id', string='Shipment Details', copy=True)
    reference = fields.Char("Reference No", required=True, copy=False, readonly=True, default='New')
    name = fields.Char(required=True)
    image = fields.Binary()
    lot = fields.Char()
    year = fields.Selection(year_range, string='Year', required=True)
    make = fields.Char()
    category = fields.Many2one('cds.vehicle.category', string='Category')
    model = fields.Char(required=True)
    sub_model = fields.Char()
    trim_level = fields.Text()
    location = fields.Char()
    key = fields.Boolean(required=True)
    vin_number = fields.Char(required=True)
    bidding_price = fields.Monetary(string='Bidding Price', currency_field='currency', required=True)
    currency = fields.Many2one('res.currency', string='Currency', required=True)
    dealership_tax = fields.Monetary(string='Dealership Tax', currency_field='currency')
    yard = fields.Monetary(string='Yard', currency_field='currency')
    tow = fields.Monetary(string='Tow', currency_field='currency', required=True)
    Shipment = fields.Monetary(string='Shipment', currency_field='currency', required=True)
    vat = fields.Monetary(string='VAT', currency_field='currency', required=True)
    custom = fields.Monetary(string='Custom', currency_field='currency', required=True)
    port_clearance_fee = fields.Monetary(string='Port Clearance Fee', currency_field='currency', required=True)
    purchase_fee = fields.Monetary(string='Purchase Agent Fee', currency_field='currency', required=True)
    recovery_fee = fields.Monetary(string='Recovery Fee', currency_field='currency', required=True)
    repairing_cost = fields.Monetary(string='Repairing Cost', currency_field='currency', required=True)
    sales_agent_fee = fields.Monetary(string='Sales Agent Fee', currency_field='currency', required=True)
    profit_margin = fields.Float(string='Profit Margin', required=True)
    status_class = fields.Char(compute='_compute_status_class', string='Status Class', store=False)
    Selling_price = fields.Monetary(string='Selling Price', currency_field='currency', compute='_compute_selling_price', store=True)
    total_cost = fields.Monetary(string='Total Cost', currency_field='currency', compute='_compute_total_cost', store=True)
    shipment_date = fields.Date(string='Shipment Date')    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('shipment_confirmed', 'Shipment Confirmed'),
        ('dock', 'Dock'),
        ('maintenance', 'Maintenance'),
        ('sold', 'Sold'),  # Add the 'sold' state
    ], string='State', default='draft')



    @api.constrains('profit_margin')
    def _check_profit_margin(self):
            for rec in self:
                if rec.profit_margin > 100:
                    raise ValidationError("Profit margin cannot be greater than 100.")
            

    @api.depends('bidding_price', 'dealership_tax', 'tow', 'Shipment', 'vat', 'custom', 'port_clearance_fee', 'purchase_fee', 'recovery_fee', 'repairing_cost', 'sales_agent_fee', 'Selling_price', 'profit_margin')
    def _compute_total_cost(self):
        for record in self:
            record.Selling_price = False
            total_amount = (
                record.bidding_price +
                record.dealership_tax +
                record.tow +
                record.Shipment +
                record.vat +
                record.custom +
                record.port_clearance_fee +
                record.purchase_fee +
                record.recovery_fee +
                record.repairing_cost +
                record.sales_agent_fee +
                record.Selling_price  # Include Selling Price in the total amount calculation
            )
            record.total_cost = total_amount  # Subtract Selling Price from the total amount
            # record.Selling_price = ((record.total_cost * record.profit_margin)/100) + record.total_cost

    @api.depends('total_cost')
    def _compute_selling_price(self):
        for rec in self:
            rec.Selling_price = rec.total_cost * rec.profit_margin + rec.total_cost


    

    def action_trigger_shipment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipment Wizard',
            'res_model': 'shipment.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }


    @api.depends('state')
    def _compute_status_class(self):
        for record in self:
            record.status_class = f'o_status_{record.state}'

    def action_mark_won(self):
        for record in self:
            record.state = 'won'

    def action_mark_lost(self):
        for record in self:
            record.state = 'lost'

    def action_mark_draft(self):
        for record in self:
            record.state = 'draft'

    def action_mark_dock(self):
        for record in self:
            record.state = 'dock'

    def action_trigger_maintenance(self):
        for record in self:
            if record.state == 'dock':
                record.state = 'maintenance'

    def action_mark_sold(self):
        for record in self:
            record.state = 'sold'

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('cds.vehicle.sequence')
        return super(Vehicle, self).create(vals)



    activity_ids = fields.One2many(
        'mail.activity',
        'res_id',
        domain=lambda self: [('res_model', '=', 'cds.vehicle')],
        string='Activities',
        auto_join=True,
        help="Activities related to this vehicle",
    )

    message_follower_ids = fields.Many2many(
        'mail.followers',
        'mail_followers_rel',
        'res_id',
        'partner_id',
        string="Followers",
        copy=False,
    )

    message_ids = fields.One2many(
        'mail.message',
        'res_id',
        domain=lambda self: [('model', '=', 'cds.vehicle')],
        string='Messages',
        auto_join=True,
        help="Messages and communication history",
    )





class ShipmentDetails(models.Model):
    _name = 'shipment.details'
    _description = 'Shipment Details'

    vehicle_id = fields.Many2one('cds.vehicle', string='Vehicle', required=True, ondelete='cascade')
    shipment_date = fields.Date(string='Shipment Date', required=True, default=fields.Date.context_today)
    origin_port = fields.Char(string='Origin Port', required=True)
    destination_port = fields.Char(string='Destination Port', required=True)
    expected_arrival_date = fields.Date(string='Expected Arrival Date', required=True)
    tracking_number = fields.Char(string='Tracking Number', required=True)
    transportation_company = fields.Char(string='Transportation Company', required=True)


class VehicleCategory(models.Model):
    _name = 'cds.vehicle.category'
    _description = 'Vehicle Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
