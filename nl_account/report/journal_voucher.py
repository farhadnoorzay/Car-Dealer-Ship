from odoo import models
from odoo.exceptions import UserError

class JournalVoucherReport(models.AbstractModel):
    _name = 'report.nl_account.report_journal_voucher'
    _description = "Journal Voucher Report"

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('nl_account.report_journal_voucher')
        journals = self.env[report.model].browse(docids)
        if not journals:
            raise UserError("Only Journal Entries can be printed.")
            
        return {
            'docs': journals,
            'all_journals': journals, 
            'doc_model': report.model,
        }