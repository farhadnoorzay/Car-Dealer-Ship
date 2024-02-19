# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.addons.mail.models import mail_thread as MailThread
from odoo.exceptions import ValidationError







year_range = [(str(year), str(year)) for year in range(2000, 2026)]

class Vehicle(models.Model):
    _name = 'cds.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]
    _rec_name = 'reference'

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
    selling_price = fields.Monetary(string='Selling Price', currency_field='currency', compute='_compute_selling_price', store=True)
    total_cost = fields.Monetary(string='Total Cost', currency_field='currency', compute='_compute_total_cost', store=True)

    
    original_bidding_price = fields.Monetary(string='Bidding Price', currency_field='currency', required=True)
    original_currency = fields.Many2one('res.currency', string='Currency')
    original_dealership_tax = fields.Monetary(string='Dealership Tax', currency_field='currency')
    original_yard = fields.Monetary(string='Yard', currency_field='currency')
    original_tow = fields.Monetary(string='Tow', currency_field='currency', required=True)
    original_Shipment = fields.Monetary(string='Shipment', currency_field='currency', required=True)
    original_vat = fields.Monetary(string='VAT', currency_field='currency', required=True)
    original_custom = fields.Monetary(string='Custom', currency_field='currency', required=True)
    original_port_clearance_fee = fields.Monetary(string='Port Clearance Fee', currency_field='currency', required=True)
    original_purchase_fee = fields.Monetary(string='Purchase Agent Fee', currency_field='currency', required=True)
    original_recovery_fee = fields.Monetary(string='Recovery Fee', currency_field='currency', required=True)
    original_repairing_cost = fields.Monetary(string='Repairing Cost', currency_field='currency', required=True)
    original_sales_agent_fee = fields.Monetary(string='Sales Agent Fee', currency_field='currency', required=True)
    original_status_class = fields.Char(compute='_compute_original_status_class', string='Status Class', store=False)
    original_profit_margin = fields.Float(string='Profit Margin', required=True)
    original_selling_price = fields.Monetary(string='Selling Price', currency_field='currency', compute='_compute_original_selling_price', store=True)
    original_total_cost = fields.Monetary(string='Total Cost', currency_field='currency', compute='_compute_original_total_cost', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('won', 'Won'),
        ('shipment_confirmed', 'Shipment Confirmed'),
        ('dock', 'Dock'),
        ('maintenance', 'Maintenance'),
        ('sold', 'Sold'),  # Add the 'sold' state
        ('lost', 'Lost'),
    ], string='State', default='draft', group_expand='_expand_states')



    @api.constrains('profit_margin')
    def _check_profit_margin(self):
            for rec in self:
                if rec.profit_margin > 100:
                    raise ValidationError("Profit margin cannot be greater than 100.")
            

    @api.depends('bidding_price', 'dealership_tax','yard', 'tow', 'Shipment', 'vat', 'custom', 'port_clearance_fee', 'purchase_fee', 'recovery_fee', 'repairing_cost', 'sales_agent_fee', 'profit_margin')
    def _compute_total_cost(self):
        for record in self:
            total_amount = (
                record.bidding_price +
                record.dealership_tax +
                record.yard +
                record.tow +
                record.Shipment +
                record.vat +
                record.custom +
                record.port_clearance_fee +
                record.purchase_fee +
                record.recovery_fee +
                record.repairing_cost +
                record.sales_agent_fee # Include Selling Price in the total amount calculation
            )
            record.total_cost = total_amount  # Subtract Selling Price from the total amount
            # record.Selling_price = ((record.total_cost * record.profit_margin)/100) + record.total_cost

    @api.depends('total_cost')
    def _compute_selling_price(self):
        for rec in self:
            rec.selling_price = rec.total_cost * rec.profit_margin + rec.total_cost


    @api.depends('original_bidding_price','original_dealership_tax', 'original_yard', 'original_tow', 'original_Shipment', 'original_vat', 'original_custom', 'original_port_clearance_fee', 'original_purchase_fee', 'original_recovery_fee', 'original_repairing_cost', 'original_sales_agent_fee', 'original_profit_margin')
    def _compute_original_total_cost(self):
        for record in self:
            total_amount = (
                record.original_bidding_price +
                record.original_dealership_tax +
                record.original_yard +
                record.original_tow +
                record.original_Shipment +
                record.original_vat +
                record.original_custom +
                record.original_port_clearance_fee +
                record.original_purchase_fee +
                record.original_recovery_fee +
                record.original_repairing_cost +
                record.original_sales_agent_fee # Include Selling Price in the total amount calculation
            )
            record.original_total_cost = total_amount  # Subtract Selling Price from the total amount
            # record.Selling_price = ((record.total_cost * record.profit_margin)/100) + record.total_cost

    @api.depends('original_total_cost')
    def _compute_original_selling_price(self):
        for rec in self:
            rec.original_selling_price = rec.original_total_cost * rec.original_profit_margin + rec.original_total_cost




    @api.depends('state')
    def _compute_status_class(self):
        for record in self:
            record.status_class = f'o_status_{record.state}'

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'

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

    # def action_reset_to_draft(self):
    #     for record in self:
    #         if record.state == 'dock':
    #             record.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('cds.vehicle.sequence')
        return super(Vehicle, self).create(vals)

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
    

class VehicleCategory(models.Model):
    _name = 'cds.vehicle.category'
    _description = 'Vehicle Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
