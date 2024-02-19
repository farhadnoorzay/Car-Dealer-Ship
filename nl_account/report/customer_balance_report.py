from odoo import models, _
from odoo.exceptions import ValidationError
from odoo.addons.nl_account.helpers import accounts


class CustomerBalanceReport(models.AbstractModel):
    _name = 'report.nl_account.customer_balance_report_template'

    def _get_report_values(self, docids, data=None):
        wizard_id = self.env['customer.balance.wizard'].browse(data.get('wizard_id'))
        return {
            'wizard_id':wizard_id,
            'report_data': data.get('report_data'),
        }
    
class CustomerBalanceReportXls(models.AbstractModel):
    _name = 'report.nl_account.customer_balance_report_xls'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        wizard_id = self.env['customer.balance.wizard'].browse(data.get('wizard_id'))
        report_data = data.get('report_data')
        balance_as_of = data.get('date')

        headers = ['Partner'] + wizard_id.currency_ids.mapped('name')
        FONT_SIZE = 10
        NORMAL_FORMAT = workbook.add_format({'font_size': FONT_SIZE, 'align': 'center', 'valign': 'vcenter'})
        BOLD_FORMAT_GRAY = workbook.add_format({'font_size': FONT_SIZE, 'bold': True, 'bg_color': '#D3D3D3', 'align': 'center', 'valign': 'vcenter'})
        BOLD_FORMAT_NORMAL = workbook.add_format({'font_size': FONT_SIZE, 'bold': True})
        HEADING_FORMAT = workbook.add_format({
                'bold':     True,
                'border':   6,
                'align':    'center',
                'valign':   'vcenter',
                'fg_color': '#D7E4BC',
            })

        sheet = workbook.add_worksheet(f'Partners Balance')
        sheet.set_portrait()
        sheet.set_paper(4)
        sheet.center_horizontally()
        row = 0
        sheet.merge_range(row, 0, 0, len(headers) - 1, f'Partners Balance', HEADING_FORMAT)

        row += 1
        sheet.write(row,0,'Balance as of', BOLD_FORMAT_NORMAL)
        sheet.write(row,1, balance_as_of, BOLD_FORMAT_NORMAL)

        row += 1
        col = 0
        for header in headers:
            sheet.write(row,col,header, BOLD_FORMAT_GRAY)
            col += 1

        for partner in report_data:
            row += 1
            for currency_id in wizard_id.currency_ids:
                currency_name = currency_id.name
                balance = report_data[partner][currency_name]

                if currency_id.position=='before':
                    balance_format=f'[${currency_id.symbol}]#,##0.00'
                else:
                    balance_format= f'#,##0.00 [${currency_id.symbol}]'
                money_format = workbook.add_format({'num_format':balance_format,'font_size': FONT_SIZE,'align':'center','valign':'vcenter'})

                sheet.write(row, 0, report_data[partner]['partner_name'], NORMAL_FORMAT)
                sheet.write_number(row, headers.index(currency_name), balance,money_format)

        sheet.set_column(1, 0, 20)
        sheet.set_column(1, 1, 11)
