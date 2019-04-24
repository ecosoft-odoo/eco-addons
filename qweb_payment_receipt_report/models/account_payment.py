# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def get_invoice_lines(self):
        self.ensure_one()
        invoice_line_ids = self.env['account.invoice.line'].search(
            [('invoice_id', 'in', self.invoice_ids.ids)])
        return invoice_line_ids
