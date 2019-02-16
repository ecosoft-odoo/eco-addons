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
    def post(self):
        for payment in self:
            if payment.taxinv_ready:
                payment._check_tax_invoice_manual()
        res = super().post()
        self.mapped('tax_line_ids').write({'tax_invoice_manual': False})
        return res

    @api.multi
    def clear_tax_cash_basis(self):
        for payment in self:
            # Validation
            if not payment.pending_tax_cash_basis_entry:
                raise UserError(_('Tax cash basis is no longer pending.'))
            if not payment.taxinv_ready:
                raise UserError(_('Tax Invoice Ready is not checked.'))
            payment._check_tax_invoice_manual()
            payment.pending_tax_cash_basis_entry = False
            # Find move for this payment tax to clear, post it
            moves = payment.tax_line_ids.\
                mapped('move_line_ids').mapped('move_id')
            for move in moves:
                if move.state == 'draft':
                    move.post()
        self.mapped('tax_line_ids').write({'tax_invoice_manual': False})
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

    @api.multi
    def _check_tax_invoice_manual(self):
        for payment in self:
            no_taxinv_lines = payment.tax_line_ids.\
                filtered(lambda l: not l.tax_invoice_manual)
            if no_taxinv_lines:
                raise UserError(_('Some tax invoice number is not filled!'))

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
            payment._check_tax_invoice_manual()
