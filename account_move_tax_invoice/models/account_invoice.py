# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    tax_invoice_manual = fields.Char(
        string='Tax Invoice',
        copy=False,
        help="Used for purchase invoice, when vendor will provice number\n"
        "this will always overwrite invoice's number",
    )
    tax_invoice = fields.Char(
        string='Tax Invoice',
        compute='_compute_tax_invoice',
        help="- case sales invoice/refund, use invoice number\n"
        "- case purchase invoice/refund, user will manually keyin\n",
    )

    @api.multi
    def _compute_tax_invoice(self):
        """ tax_invoice_manual over vendor inv ref over cust inv number """
        for tax_line in self:
            tax_line.tax_invoice = tax_line.tax_invoice_manual or \
                tax_line.invoice_id.reference or \
                tax_line.invoice_id.number
        return True
