# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _name = 'sale.make.planned.invoice'

    @api.multi
    def create_invoices_by_plan(self):
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        sale.ensure_one()
        MakeInvoice = self.env['sale.advance.payment.inv']
        invoice_plans = sale.invoice_plan_ids.filtered('to_invoice')
        for plan in invoice_plans:
            makeinv_wizard = {'advance_payment_method': 'all'}
            if plan.type == 'advance':
                makeinv_wizard['advance_payment_method'] = 'percentage'
                makeinv_wizard['amount'] = plan.percent
            makeinvoice = MakeInvoice.create(makeinv_wizard)
            makeinvoice.with_context(invoice_plan_id=plan.id).create_invoices()
        if self._context.get('open_invoices', False):
            return sale.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
