# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Tax Invoice Columns in Journal Items",
    'version': "11.0.0.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    'description': """
    This module provide more flexibility on registering tax invoice number
    for both sales / purchase case
    """,
    'website': "http://ecosoft.co.th",
    'category': "Localization / Accounting",
    'license': "AGPL-3",
    'depends': ["account",
                "account_invoice_tax_hook"],
    'data': ["views/account_invoice.xml",
             "views/account_payment_view.xml"],
    'installable': True,
}
