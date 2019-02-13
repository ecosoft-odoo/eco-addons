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


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    def create_tax_cash_basis_entry(self, percentage_before_rec):
        """ Add 1 Hook Point """
        self.ensure_one()
        move_date = self.debit_move_id.date
        newly_created_move = self.env['account.move']
        for move in (self.debit_move_id.move_id, self.credit_move_id.move_id):
            # move_date is the max of the 2 reconciled items
            if move_date < move.date:
                move_date = move.date
            for line in move.line_ids:
                # ========= MonkeyPatch HOOK =========
                self = self.with_context(cash_basis_entry_hook=line)
                # ====================================
                # TOCHECK: normal and cash basis taxes shoudn't be mixed
                # together (on the same invoice line for example) as it will
                # create reporting issues. Not sure of the behavior to
                # implement in that case, though.
                if not line.tax_exigible:
                    percentage_before = percentage_before_rec[move.id]
                    percentage_after = line._get_matched_percentage()[move.id]
                    # amount is the current cash_basis amount minus the one
                    # before the reconciliation
                    amount = line.balance * percentage_after - \
                        line.balance * percentage_before
                    rounded_amt = self._get_amount_tax_cash_basis(amount, line)
                    if float_is_zero(rounded_amt, precision_rounding=line.
                                     company_id.currency_id.rounding):
                        continue
                    if line.tax_line_id and line.tax_line_id.\
                            tax_exigibility == 'on_payment':
                        if not newly_created_move:
                            newly_created_move = self._create_tax_basis_move()
                        # create cash basis entry for the tax line
                        to_clear_aml = self.env['account.move.line'].\
                            with_context(check_move_validity=False).create({
                                'name': line.move_id.name,
                                'debit': abs(rounded_amt) if
                                rounded_amt < 0 else 0.0,
                                'credit': rounded_amt if
                                rounded_amt > 0 else 0.0,
                                'account_id': line.account_id.id,
                                'tax_exigible': True,
                                'amount_currency': line.amount_currency and
                                line.currency_id.round(
                                    -line.amount_currency * amount /
                                    line.balance) or 0.0,
                                'currency_id': line.currency_id.id,
                                'move_id': newly_created_move.id,
                                'partner_id': line.partner_id.id,
                            })
                        # Group by cash basis account and tax
                        self.env['account.move.line'].\
                            with_context(check_move_validity=False).create({
                                'name': line.name,
                                'debit': rounded_amt if
                                rounded_amt > 0 else 0.0,
                                'credit': abs(rounded_amt) if
                                rounded_amt < 0 else 0.0,
                                'account_id':
                                line.tax_line_id.cash_basis_account.id,
                                'tax_line_id': line.tax_line_id.id,
                                'tax_exigible': True,
                                'amount_currency': line.amount_currency and
                                line.currency_id.round(
                                    line.amount_currency * amount /
                                    line.balance) or 0.0,
                                'currency_id': line.currency_id.id,
                                'move_id': newly_created_move.id,
                                'partner_id': line.partner_id.id,
                            })
                        if line.account_id.reconcile:
                            # setting the account to allow reconciliation
                            # will help to fix rounding errors
                            to_clear_aml |= line
                            to_clear_aml.reconcile()

                    if any([tax.tax_exigibility == 'on_payment'
                            for tax in line.tax_ids]):
                        if not newly_created_move:
                            newly_created_move = self._create_tax_basis_move()
                        # create cash basis entry for the base
                        for tax in line.tax_ids:
                            account_id = self.\
                                _get_tax_cash_basis_base_account(line, tax)
                            self.env['account.move.line'].with_context(
                                check_move_validity=False).create({
                                    'name': line.name,
                                    'debit': rounded_amt > 0 and
                                    rounded_amt or 0.0,
                                    'credit': rounded_amt < 0
                                    and abs(rounded_amt) or 0.0,
                                    'account_id': account_id.id,
                                    'tax_exigible': True,
                                    'tax_ids': [(6, 0, [tax.id])],
                                    'move_id': newly_created_move.id,
                                    'currency_id': line.currency_id.id,
                                    'amount_currency': self.amount_currency and
                                    line.currency_id.round(
                                        line.amount_currency * amount /
                                        line.balance) or 0.0,
                                    'partner_id': line.partner_id.id,
                                })
                            self.env['account.move.line'].with_context(
                                check_move_validity=False).create({
                                    'name': line.name,
                                    'credit': rounded_amt > 0 and
                                    rounded_amt or 0.0,
                                    'debit': rounded_amt < 0 and
                                    abs(rounded_amt) or 0.0,
                                    'account_id': account_id.id,
                                    'tax_exigible': True,
                                    'move_id': newly_created_move.id,
                                    'currency_id': line.currency_id.id,
                                    'amount_currency': self.amount_currency and
                                    line.currency_id.round(
                                        -line.amount_currency * amount /
                                        line.balance) or 0.0,
                                    'partner_id': line.partner_id.id,
                                })
        if newly_created_move:
            if move_date > (self.company_id.period_lock_date or '0000-00-00') \
                    and newly_created_move.date != move_date:
                # The move date should be the maximum date between
                # payment and invoice (in case
                # of payment in advance). However, we should make sure
                # the move date is not
                # recorded before the period lock date as the tax statement
                # for this period is
                # probably already sent to the estate.
                newly_created_move.write({'date': move_date})
            # post move
            newly_created_move.post()
