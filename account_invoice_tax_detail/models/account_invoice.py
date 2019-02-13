# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_tax_line_vals(self, line, tax):
        """ Add invl_id to account.invoice.tax """
        vals = super()._prepare_tax_line_vals(line, tax)
        vals['invl_id'] = line.id
        return vals

    def write(self, vals):
        """ For invl_id to works on create iline, ensure tax recompute """
        res = super().write(vals)
        for line in vals.get('invoice_line_ids', []):
            if line[2] and line[2].get('invoice_line_tax_ids'):
                self.compute_taxes()
                return res
        return res

    @api.model
    def create(self, vals):
        """ For invl_id to works on create iline, ensure tax recompute """
        rec = super().create(vals)
        rec.compute_taxes()
        return rec


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    invl_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Invoice Line',
        ondelete='cascade',
        domain="[('invoice_id', '=', invoice_id)]",
    )

    @api.model
    def _prepare_tax_line_compute_base(self, tax):
        """ account.invoice.tax will contain invoice line, for more detail """
        vals = super()._prepare_tax_line_compute_base(tax)
        vals['invl_id'] = tax.invl_id.id
        return vals
