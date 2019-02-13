# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Invoice Tax Detail",
    'version': "11.0.0.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    'website': "http://ecosoft.co.th",
    'category': "Localization / Accounting",
    'license': "AGPL-3",
    'depends': ["account",
                "account_invoice_tax_hook"],
    'data': ["views/account_invoice.xml"],
    'installable': True,
}
