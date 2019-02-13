# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def _create_payment_entry(self, amount):
        if self.payment_type == 'inbound':  # Customer Payment
            self.taxinv_ready = True
        elif self.payment_type == 'outbound':  # Supplier Payment
            invoice_lines = self.invoice_ids.mapped('invoice_line_ids')
            taxes = invoice_lines.mapped('invoice_line_tax_ids')
            if not taxes.filtered(lambda l: l.tax_exigibility == 'on_payment'):
                self.taxinv_ready = True
        return super()._create_payment_entry(amount)

    @api.multi
    def clear_tax_cash_basis(self):
        for payment in self:
            if not payment.pending_tax_cash_basis_entry:
                raise UserError(_('Tax cash basis is no longer pending.'))
            if not payment.taxinv_ready:
                raise UserError(_('Tax Invoice Ready is not checked.'))
            payment._clear_tax_cash_basis_entry()
        return True

    @api.multi
    def _clear_tax_cash_basis_entry(self):
        self.ensure_one()
        full_recs = self.move_line_ids.mapped('full_reconcile_id')
        for full_rec in full_recs:
            lines = full_rec.reconciled_line_ids
            # TODO: Still unsure how to get this percentage correctly
            # Now it only works for full payment
            percentage_before_rec = lines._get_matched_percentage()
            percentage_before_rec = {x: 0.0 for x in percentage_before_rec}
            part_recs = full_rec.mapped('partial_reconcile_ids')
            for part_rec in part_recs:
                part_rec.create_tax_cash_basis_entry(percentage_before_rec)
        self.pending_tax_cash_basis_entry = False
        return True


class AccuntAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    pending_tax_cash_basis_entry = fields.Boolean(
        default=False,
        help="If pending, payment will has button to clear tax cash basis",
    )
    taxinv_ready = fields.Boolean(
        string="Tax Invoice Ready",
        default=False,
        help="Tax invoice number is ready for filling in,\n"
        "system will open tax table allow user to fill in",
    )
    tax_line_ids = fields.Many2many(
        comodel_name='account.invoice.tax',
        copy=False,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        invoice_ids = self._context.get('active_ids')
        InvoiceTax = self.env['account.invoice.tax']
        tax_lines = InvoiceTax.search([('invoice_id', 'in', invoice_ids)])
        res['tax_line_ids'] = [(6, 0, tax_lines.ids)]
        return res

    @api.constrains('taxinv_ready', 'pending_tax_cash_basis_entry')
    def _check_tax_invoice(self):
        for payment in self:
            if not payment.taxinv_ready or \
                    not payment.pending_tax_cash_basis_entry:
                continue
            no_taxinv_lines = payment.tax_line_ids.\
                filtered(lambda l: not l.tax_invoice_manual)
            if no_taxinv_lines:
                raise UserError(_('Some tax invoice number is not filled!'))
