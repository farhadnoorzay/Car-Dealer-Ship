# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Vehicle(models.Model):
    _inherit = 'cds.vehicle'

    shipment_id = fields.Many2one('shipment.details')
    shipment_reference = fields.Char(string='Shipment Reference', related='shipment_id.reference')
    shipment_date = fields.Date(string='Shipment Date', related='shipment_id.shipment_date')
    origin_port = fields.Char(string='Origin Port', related='shipment_id.origin_port')
    destination_port = fields.Char(string='Destination Port', related='shipment_id.destination_port')
    expected_arrival_date = fields.Date(string='Expected Arrival Date', related='shipment_id.expected_arrival_date')
    tracking_number = fields.Char(string='Tracking Number', related='shipment_id.tracking_number')
    transportation_company = fields.Char(string='Transportation Company', related='shipment_id.transportation_company')

    def action_trigger_shipment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipment Wizard',
            'res_model': 'shipment.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }