# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round as round


class SaleOder(models.Model):
    _inherit = 'sale.order'

    invoice_plan_ids = fields.One2many(
        comodel_name='sale.invoice.plan',
        inverse_name='sale_id',
        string='Inovice Plan',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    use_invoice_plan = fields.Boolean(
        string='Use Invoice Plan',
        default=False,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.constrains('state')
    def _check_invoice_plan(self):
        for rec in self:
            if rec.state != 'draft':
                if rec.invoice_plan_ids.filtered(lambda l: not l.percent):
                    raise UserError(
                        _('Please fill percentage for all invoice plan lines'))

    @api.multi
    def create_invoice_plan(self, num_installment, installment_date,
                            interval, interval_type, advance):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        invoice_plans = []
        if num_installment <= 1:
            raise UserError(_('Number Installment must greater than 1'))
        Decimal = self.env['decimal.precision']
        prec = Decimal.precision_get('Product Unit of Measure')
        percent = round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment-1))
        # Advance
        if advance:
            vals = {'installment': 0, 'plan_date': installment_date,
                    'type': 'advance', 'percent': 0.0}
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(installment_date,
                                               interval, interval_type)
        # Normal
        for i in range(num_installment):
            this_installment = i+1
            if num_installment == this_installment:
                percent = percent_last
            vals = {'installment': this_installment,
                    'plan_date': installment_date,
                    'type': 'installment',
                    'percent': percent}
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(installment_date,
                                               interval, interval_type)
        self.write({'invoice_plan_ids': invoice_plans})
        return True

    @api.multi
    def remove_invoice_plan(self):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == 'month':
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == 'year':
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        inv_ids = super().action_invoice_create(grouped=grouped, final=final)
        invoice_plan_id = self._context.get('invoice_plan_id')
        if invoice_plan_id:
            plan = self.env['sale.invoice.plan'].browse(invoice_plan_id)
            invoices = self.env['account.invoice'].browse(inv_ids)
            invoices.ensure_one()  # Expect 1 invoice for 1 invoice plan
            plan._compute_new_invoice_quantity(invoices[0])
            plan.invoice_ids += invoices

        return inv_ids


class SaleInvoicePlan(models.Model):
    _name = 'sale.invoice.plan'
    _order = 'installment'

    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sales Order',
        index=True,
        readonly=True,
        ondelete='cascade',
    )
    installment = fields.Integer(
        string='Installment',
    )
    plan_date = fields.Date(
        string='Plan Date',
        required=True,
    )
    type = fields.Selection(
        [('advance', 'Advance'),
         ('installment', 'Installment'), ],
        string='Type',
        required=True,
        default='installment',
    )
    last = fields.Boolean(
        string='Last Installment',
        compute='_compute_last',
        help="Last installment will create invoice use remaining amount",
    )
    percent = fields.Float(
        string='Percent',
        digits=dp.get_precision('Product Unit of Measure'),
        help="This percent will be used to calculate new quantity"
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        relation="sale_invoice_plan_invoice_rel",
        column1='plan_id', column2='invoice_id',
        string='Invoices',
        readonly=True,
    )
    to_invoice = fields.Boolean(
        string='Next Invoice',
        compute='_compute_to_invoice',
        help="If this line is ready to create new invoice",
    )
    invoiced = fields.Boolean(
        string='Invoice Created',
        compute='_compute_invoiced',
        help="If this line already invoiced",
    )
    _sql_constraint = [('unique_instalment',
                        'UNIQUE (sale_id, installment)',
                        'Installment must be unique on invoice plan')]

    @api.multi
    def _compute_to_invoice(self):
        """ If any invoice is in draft/open/paid do not allow to create inv
            Only if previous to_invoice is False, it is eligible to_invoice
        """
        for rec in self.sorted('installment'):
            rec.to_invoice = False
            if rec.sale_id.state != 'sale':  # Not confirmed, no to_invoice
                continue
            if not rec.invoiced:
                rec.to_invoice = True
                break

    @api.multi
    def _compute_invoiced(self):
        for rec in self:
            invoiced = rec.invoice_ids.filtered(
                lambda l: l.state in ('draft', 'open', 'paid'))
            rec.invoiced = invoiced and True or False

    @api.multi
    def _compute_last(self):
        for rec in self:
            last = max(rec.sale_id.invoice_plan_ids.mapped('installment'))
            rec.last = rec.installment == last

    @api.multi
    def _compute_new_invoice_quantity(self, invoice):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        for line in invoice.invoice_line_ids:
            assert len(line.sale_line_ids) >= 0, \
                'No matched order line for invoice line'
            order_line = line.sale_line_ids[0]
            if order_line.is_downpayment:
                line.quantity = -percent/100  # Always based on 1 unit
            else:
                line.quantity = order_line.product_uom_qty * (percent/100)
        invoice.compute_taxes()
