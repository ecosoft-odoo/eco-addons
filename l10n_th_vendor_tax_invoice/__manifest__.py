# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Thai Localization - Vendor Tax Invoice",
    'version': "12.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    'description': """

In Thailand, tax invoice number from vendor can be receieved even after
payment is paid in Odoo.

This module add payment.tax.invoice table in payment document, allow user
to come in after to register tax invoice number / date and then Clear VAT.

    """,
    'website': "http://ecosoft.co.th",
    'category': "Localization / Accounting",
    'license': "AGPL-3",
    'depends': ["account",
                "account_create_tax_cash_basis_entry_hook"],
    'data': ["security/ir.model.access.csv",
             "views/account_invoice.xml",
             "views/account_payment_view.xml"],
    'installable': True,
}
