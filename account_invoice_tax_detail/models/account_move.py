# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invl_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Invoice Line',
        copy=False,
        ondelete='restrict',
    )

    @api.multi
    def _filter_invoice_tax_detail(self, move_line):
        return super()._filter_invoice_tax_detail(move_line).\
            filtered(lambda line: move_line.invl_id == line.invl_id)

    @api.model
    def create(self, vals):
        if self._context.get('cash_basis_tax_detail', False):
            move_line = self._context['cash_basis_entry_hook']
            vals.update({
                'invoice_id': move_line.invoice_id.id,
                'invl_id': move_line.invl_id.id,
            })
        return super().create(vals)
