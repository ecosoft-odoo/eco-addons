# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _filter_invoice_tax_detail(self, move_line):
        """ Hook Function """
        return self

    @api.depends('move_id.line_ids', 'move_id.line_ids.tax_line_id',
                 'move_id.line_ids.debit', 'move_id.line_ids.credit')
    def _compute_tax_base_amount(self):
        """ Add 1 Hook Point """
        for move_line in self:
            if move_line.tax_line_id:
                base_lines = move_line.move_id.line_ids.filtered(
                    lambda line: move_line.tax_line_id in line.tax_ids)
                # ==== MonkeyPatch HOOK ===
                base_lines = base_lines._filter_invoice_tax_detail(move_line)
                # =========================
                move_line.tax_base_amount = \
                    abs(sum(base_lines.mapped('balance')))
            else:
                move_line.tax_base_amount = 0
