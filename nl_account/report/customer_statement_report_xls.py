
from odoo import models, fields, api
from datetime import datetime ,timedelta

class FosterReportXls(models.AbstractModel):
    _name = 'report.nl_account.customer_statement_report_xls'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data,records):
        wizard_id = self.env['customer.statement.wizard'].browse(data.get('wizard_id'))
        report_data = data.get('data')
        opening_balance = data.get('opening_balance')
        balance = data.get('balance')
        total_debits = data.get('total_debits')
        total_credits = data.get('total_credits')
        closing_balance = data.get('closing_balance')

        headers = ['Reference','Date','Label','Debit','Credit','Balance']

        FONT_SIZE = 10
        NORMAL_FORMAT = workbook.add_format({'font_size': FONT_SIZE,'align':'center','valign':'vcenter'})
        
        BOLD_FORMAT_GRAY = workbook.add_format({'font_size': FONT_SIZE, 'bold': True, 'bg_color': '#D3D3D3','align':'center','valign':'vcenter'})
        BOLD_FORMAT_NORMAL = workbook.add_format({'font_size': FONT_SIZE, 'bold': True})

        format=''
        currency_id = wizard_id.currency_id
        # [$$]#,##0.00;-[$$]#,##0.00
        # #,##0 [$Afs];-#,##0 [$Afs]
        if currency_id.position=='before':
             format=f'[${currency_id.symbol}]#,##0.00'
        else:
             format= f'#,##0.00 [${currency_id.symbol}]'

        money_format = workbook.add_format({'num_format':format,'font_size': FONT_SIZE,'align':'center','valign':'vcenter'})
        HEADING_FORMAT = workbook.add_format({
                'bold':     True,
                'border':   6,
                'align':    'center',
                'valign':   'vcenter',
                'fg_color': '#D7E4BC',
            })

        sheet = workbook.add_worksheet(f'Partner Statement-{wizard_id.partner_id.sequence}|{wizard_id.partner_id.name} ')
        sheet.set_portrait()
        sheet.set_paper(4)
        sheet.center_horizontally()
        
        row =0
        sheet.merge_range(row,0,0,len(headers)-1,f'Partner Statement',HEADING_FORMAT)
        
        row+=1
        sheet.write(row, 0, 'Period',BOLD_FORMAT_NORMAL)
        sheet.write(row, 1, f'{wizard_id.from_date}/{wizard_id.to_date}',NORMAL_FORMAT)
        
        row+=1
        sheet.write(row, 0, 'Partner',BOLD_FORMAT_NORMAL)
        sheet.write(row, 1, f'{wizard_id.partner_id.sequence}|{wizard_id.partner_id.name}',NORMAL_FORMAT)
        
        row+=1
        sheet.write(row, 0, 'Currency',BOLD_FORMAT_NORMAL)
        sheet.write(row, 1, f'{wizard_id.currency_id.name}',NORMAL_FORMAT)

        row+=2
        for col, header in enumerate(headers):
                sheet.write(row, col, header,BOLD_FORMAT_GRAY)
                sheet.set_column(col, col, 15)
         
        col = 0  

        for record in report_data:
            row += 1
            col = 0
            sheet.write(row, col, record['name'], NORMAL_FORMAT)
            col += 1
            sheet.write(row, col, record['date'], NORMAL_FORMAT)
            col += 1
            sheet.write(row, col, record['label'], NORMAL_FORMAT)
            col += 1
            sheet.write_number(row, col, record['debit'], money_format)
            col += 1
            sheet.write_number(row, col, record['credit'], money_format)
            col += 1
            sheet.write_number(row, col, record['balance'], money_format)

        row+=1
        sheet.merge_range(row,0,row,2,'Total',BOLD_FORMAT_GRAY)
        sheet.write_number(row, 3, total_debits, money_format)
        sheet.write_number(row, 4, total_credits, money_format)
        sheet.write_number(row, 5, balance, money_format)

        row+=2
        sheet.write(row, len(headers)-2, 'Opening Balance',BOLD_FORMAT_NORMAL)
        sheet.write(row, len(headers)-1, opening_balance,money_format)
        
        row+=1
        sheet.write(row, len(headers)-2, 'Closing Balance',BOLD_FORMAT_NORMAL)
        sheet.write(row, len(headers)-1, closing_balance,money_format)

        sheet.set_column(1, 1, 20)
        sheet.set_column(3, 2, 25)
