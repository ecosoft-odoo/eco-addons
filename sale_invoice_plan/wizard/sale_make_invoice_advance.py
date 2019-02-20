# -*- coding: utf-8 -*-
import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super()._create_invoice(order, so_line, amount)
        invoice_plan_id = self._context.get('invoice_plan_id')
        if invoice_plan_id:
            plan = self.env['sale.invoice.plan'].browse(invoice_plan_id)
            plan.invoice_ids += invoice
        return invoice
