from odoo import models, fields, api

class CDSVehicleShipmentWizard(models.TransientModel):
    _name = 'shipment.wizard'
    _description = 'Shipment Wizard'



    shipment_date = fields.Date(string='Shipment Date')
    origin_port = fields.Char(string='Origin Port')
    destination_port = fields.Char(string='Destination Port')
    expected_arrival_date = fields.Date(string='Expected Arrival Date')
    tracking_number = fields.Char(string='Tracking Number')
    transportation_company = fields.Char(string='Transportation Company')
    shipment_id = fields.Many2one('shipment.details')
    
    @api.onchange('shipment_id')
    def _onchange_shipment_id(self):
        self.write({
            'shipment_date': self.shipment_id.shipment_date,
            'origin_port': self.shipment_id.origin_port,
            'destination_port': self.shipment_id.destination_port,
            'expected_arrival_date': self.shipment_id.expected_arrival_date,
            'tracking_number': self.shipment_id.tracking_number,
            'transportation_company': self.shipment_id.transportation_company
        })

    def confirm_shipment(self):
        # Retrieve the active vehicle record
        active_vehicle = self.env['cds.vehicle'].browse(self.env.context.get('active_id'))

        # Update the fields in the vehicle record based on the wizard data
        if self.shipment_id:
            self.shipment_id.vehicle_ids = [(4, active_vehicle.id)]
        else:
            self.env['shipment.details'].create({
                'shipment_date': self.shipment_date,
                'origin_port': self.origin_port,
                'destination_port': self.destination_port,
                'expected_arrival_date': self.expected_arrival_date,
                'tracking_number': self.tracking_number,
                'transportation_company': self.transportation_company,
                'vehicle_ids': [(4, active_vehicle.id)]
            })
        # active_vehicle.state = "dock"
        active_vehicle.state = "shipment_confirmed"