# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def get_grouping_key(self, invoice_tax_val):
        """ Adds invl_id to returning key """
        self.ensure_one()
        key = super().get_grouping_key(invoice_tax_val)
        key += '-' + str(invoice_tax_val['invl_id'])
        return key
