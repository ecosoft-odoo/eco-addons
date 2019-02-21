# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _name = 'sale.make.planned.invoice'

    @api.multi
    def create_invoices_by_plan(self):
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        sale.ensure_one()
        MakeInvoice = self.env['sale.advance.payment.inv']
        invoice_plans = self._context.get('all_remain_invoices') and \
            sale.invoice_plan_ids.filtered(lambda l: not l.invoiced) or \
            sale.invoice_plan_ids.filtered('to_invoice')
        if not invoice_plans:
            raise UserError(_('No Invoice Plan!'))
        for plan in invoice_plans.sorted('installment'):
            makeinv_wizard = {'advance_payment_method': 'all'}
            if plan.type == 'advance':
                makeinv_wizard['advance_payment_method'] = 'percentage'
                makeinv_wizard['amount'] = plan.percent
            makeinvoice = MakeInvoice.create(makeinv_wizard)
            makeinvoice.with_context(invoice_plan_id=plan.id).create_invoices()
        return {'type': 'ir.actions.act_window_close'}
