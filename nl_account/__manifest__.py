# -*- coding: utf-8 -*-

{
    'name': 'Accounts',
    'version': '15.0.1',
    'category': 'Accounting',
    'summary': 'Manage accounting',
    'description': """
Accounts
==================
This module manage Accounting.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': 'AGPL-3',
    'price': '',
    'currency': '',
    'depends': ['account_accountant','report_xlsx'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/mail_activity_data.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/internal_transfer_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_journal.xml',
        'views/account_account_view.xml',
        'report/payment_receipt_voucher.xml',
        'report/journal_entry_voucher.xml',
        'report/transfer_voucher.xml',
        'report/account_statement_report.xml',
        'report/customer_statement_report_pdf.xml',
        'report/customer_statement_report_xls.xml',
        'report/customer_balance_report.xml',
        'wizards/internal_transfer_fee.xml',
        'wizards/customer_balance_wizard.xml',
        'wizards/account_statement_wizard.xml',
        'wizards/customer_statement_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
