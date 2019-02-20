# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleCreateInvoicePlan(models.TransientModel):
    _name = 'sale.create.invoice.plan'

    advance = fields.Boolean(
        string='Advance on 1st Invoice',
        default=False,
    )
    num_installment = fields.Integer(
        string='Number of Installment',
        default=0,
        required=True,
    )
    installment_date = fields.Date(
        string='Installment Date',
        default=fields.Date.context_today,
        required=True,
    )
    interval = fields.Integer(
        string='Interval',
        default=1,
        required=True,
    )
    interval_type = fields.Selection(
        [('day', 'Day'),
         ('month', 'Month'),
         ('year', 'Year')],
        string='Interval Type',
        default='month',
        required=True,
    )

    @api.multi
    def sale_create_invoice_plan(self):
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        self.ensure_one()
        sale.create_invoice_plan(self.num_installment,
                                 self.installment_date,
                                 self.interval,
                                 self.interval_type,
                                 self.advance)
        return {'type': 'ir.actions.act_window_close'}
