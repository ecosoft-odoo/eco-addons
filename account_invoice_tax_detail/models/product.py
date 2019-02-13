# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        """ When creating move line from invoice, assign invl_id """
        res = super()._convert_prepared_anglosaxon_line(line, partner)
        # For tax line, now we can get also get invl_id
        TaxLine = self.env['account.invoice.tax']
        if line.get('invoice_tax_line_id'):
            tax_line = TaxLine.browse(line['invoice_tax_line_id'])
            line['invl_id'] = tax_line.invl_id.id
        res.update({'invl_id': line.get('invl_id', False)})
        return res
