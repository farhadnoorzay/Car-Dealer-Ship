from odoo import models, _
from odoo.exceptions import ValidationError
from odoo.addons.nl_account.helpers import accounts


class CustomerStatementReport(models.AbstractModel):
    _name = 'report.nl_account.customer_statement_report_template'

    def _get_report_values(self, docids, data=None):
        wizard_id = self.env['customer.statement.wizard'].browse(data.get('wizard_id'))

        return {
            'data': data.get('data'),
            'wizard_id':wizard_id,
            'balance':data.get('balance'),
            'total_credit':data.get('total_credit'),
            'total_debit':data.get('total_debit')
        }