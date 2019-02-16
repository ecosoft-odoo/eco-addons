# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super()._convert_prepared_anglosaxon_line(line, partner)
        res.update({
            'invoice_tax_line_id': line.get('invoice_tax_line_id', False),
        })
        return res
