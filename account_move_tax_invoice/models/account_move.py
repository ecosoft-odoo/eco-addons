# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_tax_line_id = fields.Many2one(
        comodel_name='account.invoice.tax',
        string='Invoice Tax Line',
        copy=False,
        ondelete='restrict',
    )
    tax_invoice_manual = fields.Char(
        string='Tax Invoice',
        copy=False,
        help="Used for purchase invoice, when vendor will provice number\n"
        "this will always overwrite invoice's number",
    )
    tax_invoice = fields.Char(
        string='Tax Invoice',
        compute='_compute_tax_invoice',
        store=True,
        help="- case sales invoice/refund, use invoice number\n"
        "- case purchase invoice/refund, user will manually keyin\n",
    )

    @api.model
    def create(self, vals):
        if self._context.get('cash_basis_entry_hook', False):
            move_line = self._context['cash_basis_entry_hook']
            vals.update({
                'invoice_tax_line_id': move_line.invoice_tax_line_id.id,
            })
        return super().create(vals)

    @api.multi
    @api.depends('tax_invoice_manual', 'invoice_id.move_id')
    def _compute_tax_invoice(self):
        """ tax_invoice_manual over invoice_tax_line_id's tax_invoice """
        for ml in self:
            ml.tax_invoice = ml.tax_invoice_manual or \
                ml.invoice_tax_line_id.tax_invoice
        return True


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model
    def create(self, vals):
        """ Check payment, if taxinv_ready is not checked,
            do not create tax cash basis entry """
        aml = []
        if vals.get('debit_move_id', False):
            aml.append(vals['debit_move_id'])
        if vals.get('credit_move_id', False):
            aml.append(vals['credit_move_id'])
        # Get value of matched percentage from both move before reconciliating
        lines = self.env['account.move.line'].browse(aml)
        payment = lines.mapped('payment_id')
        payment.ensure_one()
        if payment and not payment.taxinv_ready:
            self = self.with_context(pending_tax_cash_basis_entry=True)
            payment.pending_tax_cash_basis_entry = True
        return super().create(vals)

    @api.multi
    def create_tax_cash_basis_entry(self, percentage_before_rec):
        """ When validate outbound payment and taxinv not ready, skip it """
        if self._context.get('pending_tax_cash_basis_entry'):
            return
        return super().create_tax_cash_basis_entry(percentage_before_rec)
