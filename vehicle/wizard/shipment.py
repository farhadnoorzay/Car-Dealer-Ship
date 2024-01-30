from odoo import models, fields, api

class CDSVehicleShipmentWizard(models.TransientModel):
    _name = 'shipment.wizard'
    _description = 'Shipment Wizard'



    shipment_details_id = fields.Many2one('shipment.details', string='Shipment Details', ondelete='cascade')
    shipment_date = fields.Date(string='Shipment Date', required=True, default=fields.Date.context_today)
    origin_port = fields.Char(string='Origin Port', required=True)
    destination_port = fields.Char(string='Destination Port', required=True)
    expected_arrival_date = fields.Date(string='Expected Arrival Date', required=True)
    tracking_number = fields.Char(string='Tracking Number', required=True)
    transportation_company = fields.Char(string='Transportation Company', required=True)

    def confirm_shipment(self):
        # Retrieve the active vehicle record
        active_vehicle = self.env['cds.vehicle'].browse(self.env.context.get('active_id'))

        # Update the fields in the vehicle record based on the wizard data
        self.env['shipment.details'].create({
            'shipment_date': self.shipment_date,
            'origin_port': self.origin_port,
            'destination_port': self.destination_port,
            'expected_arrival_date': self.expected_arrival_date,
            'tracking_number': self.tracking_number,
            'transportation_company': self.transportation_company,
            'vehicle_id': active_vehicle.id
        })
        active_vehicle.state = "dock"
        # active_vehicle.state = "shipment_confirmed"


        # shipment_details_values = {
        #     'vehicle_id': active_vehicle.id,
        #     # Add other details from the wizard
        # }
        # self.env['shipment.details'].create(shipment_details_values)
        # # You can add additional logic here based on your requirements

        # # Close the wizard
        # return {'type': 'ir.actions.act_window_close'}
