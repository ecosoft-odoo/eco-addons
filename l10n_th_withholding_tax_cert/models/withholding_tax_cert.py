# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


INCOME_TAX_FORM = [('pnd1', 'PND1'),
                   ('pnd3', 'PND3'),
                   ('pnd3a', 'PND3a'),
                   ('pnd53', 'PND53'),
                   ('pnd54', 'PND54')]


WHT_CERT_INCOME_TYPE = [('1', '1. เงินเดือน ค่าจ้าง ฯลฯ 40(1)'),
                        ('2', '2. ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)'),
                        ('3', '3. ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)'),
                        ('5', '5. ค่าจ้างทำของ ค่าบริการ ฯลฯ 3 เตรส'),
                        ('6', '6. ค่าบริการ/ค่าสินค้าภาครัฐ'),
                        ('7', '7. ค่าจ้างทำของ ค่ารับเหมา'),
                        ('8', '8. ธุรกิจพาณิชย์ เกษตร อื่นๆ')]


TAX_PAYER = [('withholding', 'Withholding'),
             ('paid_one_time', 'Paid One Time')]


class WithholdingTaxCert(models.Model):
    _name = 'withholding.tax.cert'

    name = fields.Char(
        string='Number',
        readonly=True,
        related='payment_id.name',
        store=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        copy=False,
    )
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('line_ids.partner_id', '=', supplier_partner_id)]"
        # "('line_ids.account_id', 'in', wt_account_ids)]",
    )
    # wt_account_ids = fields.Many2many(
    #     comodel_name='account.move',
    #     string='Withholding Tax Account',
    #     required=True,
    #     copy=True,
    # )
    company_partner_id = fields.Many2one(
        'res.partner',
        string='Company',
        readonly=True,
        copy=False,
        default=lambda self: self.env.user.company_id.partner_id,
    )
    supplier_partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    company_taxid = fields.Char(
        related='company_partner_id.vat',
        string='Company Tax ID',
        readonly=True,
    )
    supplier_taxid = fields.Char(
        related='supplier_partner_id.vat',
        string='Supplier Tax ID',
        readonly=True,
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    wt_line = fields.One2many(
        'withholding.tax.cert.line',
        'cert_id',
        string='Withholding Line',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    tax_payer = fields.Selection(
        TAX_PAYER,
        string='Tax Payer',
        default='withholding',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )

    # Computed fields to be displayed in WHT Cert.
    x_voucher_number = fields.Char(compute='_compute_cert_fields')
    x_date_value = fields.Date(compute='_compute_cert_fields')
    x_company_name = fields.Char(compute='_compute_cert_fields')
    x_supplier_name = fields.Char(compute='_compute_cert_fields')
    x_company_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_address = fields.Char(compute='_compute_cert_fields')
    x_company_address = fields.Char(compute='_compute_cert_fields')
    x_pnd1 = fields.Char(compute='_compute_cert_fields')
    x_pnd3 = fields.Char(compute='_compute_cert_fields')
    x_pnd53 = fields.Char(compute='_compute_cert_fields')
    x__display = fields.Char(compute='_compute_cert_fields')
    x_withholding = fields.Char(compute='_compute_cert_fields')
    x_paid_one_time = fields.Char(compute='_compute_cert_fields')
    x_total_base = fields.Float(compute='_compute_cert_fields')
    x_total_tax = fields.Float(compute='_compute_cert_fields')
    x_type_1_base = fields.Float(compute='_compute_cert_fields')
    x_type_1_tax = fields.Float(compute='_compute_cert_fields')
    x_type_2_base = fields.Float(compute='_compute_cert_fields')
    x_type_2_tax = fields.Float(compute='_compute_cert_fields')
    x_type_3_base = fields.Float(compute='_compute_cert_fields')
    x_type_3_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_base = fields.Float(compute='_compute_cert_fields')
    x_type_5_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_desc = fields.Char(compute='_compute_cert_fields')
    x_type_6_base = fields.Float(compute='_compute_cert_fields')
    x_type_6_tax = fields.Float(compute='_compute_cert_fields')
    x_type_6_desc = fields.Char(compute='_compute_cert_fields')
    x_type_7_base = fields.Float(compute='_compute_cert_fields')
    x_type_7_tax = fields.Float(compute='_compute_cert_fields')
    x_type_7_desc = fields.Char(compute='_compute_cert_fields')
    x_type_8_base = fields.Float(compute='_compute_cert_fields')
    x_type_8_tax = fields.Float(compute='_compute_cert_fields')
    x_type_8_desc = fields.Char(compute='_compute_cert_fields')
    x_signature = fields.Char(compute='_compute_cert_fields')

    @api.constrains('wt_line')
    def _check_wt_line(self):
        for cert in self:
            for line in cert.wt_line:
                if line.amount != line.base * line.wt_percent / 100:
                    raise ValidationError(_('WT Base/Percent/Tax mismatch!'))

    @api.multi
    def _compute_cert_fields(self):
        for rec in self:
            company = self.env.user.company_id.partner_id
            supplier = rec.supplier_partner_id
            rec.x_voucher_number = rec.voucher_id.number
            rec.x_date_value = rec.date
            rec.x_company_name = company.name
            rec.x_supplier_name = ' '.join(list(
                filter(lambda l: l is not False, [supplier.title.name,
                                                  supplier.name])))
            rec.x_company_taxid = \
                company.vat and len(company.vat) == 13 and company.vat or ''
            rec.x_supplier_taxid = \
                supplier.vat and len(supplier.vat) == 13 and supplier.vat or ''
            rec.x_supplier_address = rec.supplier_address
            rec.x_company_address = rec.company_address
            rec.x_pnd1 = rec.income_tax_form == 'pnd1' and 'X' or ''
            rec.x_pnd3 = rec.income_tax_form == 'pnd3' and 'X' or ''
            rec.x_pnd53 = rec.income_tax_form == 'pnd53' and 'X' or ''
            rec.x_withholding = \
                rec.tax_payer == 'withholding' and 'X' or ''
            rec.x_paid_one_time = \
                rec.tax_payer == 'paid_one_time' and 'X' or ''
            rec.x_total_base = rec._get_summary_by_type('base')
            rec.x_total_tax = rec._get_summary_by_type('tax')
            rec.x_type_1_base = rec._get_summary_by_type('base', '1')
            rec.x_type_1_tax = rec._get_summary_by_type('tax', '1')
            rec.x_type_2_base = rec._get_summary_by_type('base', '2')
            rec.x_type_2_tax = rec._get_summary_by_type('tax', '2')
            rec.x_type_3_base = rec._get_summary_by_type('base', '3')
            rec.x_type_3_tax = rec._get_summary_by_type('tax', '3')
            rec.x_type_5_base = rec._get_summary_by_type('base', '5')
            rec.x_type_5_tax = rec._get_summary_by_type('tax', '5')
            rec.x_type_5_desc = rec._get_summary_by_type('desc', '5')
            rec.x_type_6_base = rec._get_summary_by_type('base', '6')
            rec.x_type_6_tax = rec._get_summary_by_type('tax', '6')
            rec.x_type_6_desc = rec._get_summary_by_type('desc', '6')
            rec.x_type_7_base = rec._get_summary_by_type('base', '7')
            rec.x_type_7_tax = rec._get_summary_by_type('tax', '7')
            rec.x_type_7_desc = rec._get_summary_by_type('desc', '7')
            rec.x_type_8_base = rec._get_summary_by_type('base', '8')
            rec.x_type_8_tax = rec._get_summary_by_type('tax', '8')
            rec.x_type_8_desc = rec._get_summary_by_type('desc', '8')
            rec.x_signature = rec.create_uid.display_name

    @api.onchange('payment_id')
    def _onchange_payment_id(self):
        """ Prepare withholding cert """
        wt_account_ids = self._context.get('wt_account_ids', [])
        self.date = self.payment_id.payment_date
        self.supplier_partner_id = self.payment_id.partner_id
        # Hook to find wt move lines
        wt_move_lines = self._get_wt_move_line(self.payment_id, wt_account_ids)
        CertLine = self.env['withholding.tax.cert.line']
        for line in wt_move_lines:
            self.wt_line += CertLine.new(self._prepare_wt_line(line))

    @api.model
    def _prepare_wt_line(self, move_line):
        """ Hook point to prepare wt_line """
        return {'amount': abs(move_line.balance),
                'ref_move_line_id': move_line.id}

    @api.model
    def _get_wt_move_line(self, payment, wt_account_ids):
        """ Hook point to get wt_move_lines """
        return payment.move_line_ids.filtered(
            lambda l: l.account_id.id in wt_account_ids)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def _get_summary_by_type(self, column, ttype='all'):
        self.ensure_one()
        wt_lines = self.wt_line
        if ttype != 'all':
            wt_lines = wt_lines.filtered(lambda l:
                                         l.wt_cert_income_type == ttype)
        if column == 'base':
            return round(sum([x.base for x in wt_lines]), 2)
        if column == 'tax':
            return round(sum([x.amount for x in wt_lines]), 2)
        if column == 'desc':
            descs = [x.wt_cert_income_desc for x in wt_lines]
            descs = filter(lambda x: x and x != '', descs)
            desc = ', '.join(descs)
            return desc

    @api.model
    def _prepare_address(self, partner):
        # TODO: XXX
        address_list = [partner.street, partner.street2, partner.city,
                        partner.township_id.name, partner.district_id.name,
                        partner.province_id.name, partner.zip, ]
        address_list = filter(lambda x: x is not False and x != '',
                              address_list)
        return ' '.join(address_list).strip()


class WithholdingTaxCertLine(models.Model):
    _name = 'withholding.tax.cert.line'

    cert_id = fields.Many2one(
        'withholding.tax.cert',
        string='WHT Cert',
        index=True,
    )
    wt_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
        required=True,
    )
    wt_cert_income_desc = fields.Char(
        string='Income Description',
        size=500,
        required=False,
    )
    base = fields.Float(
        string='Base Amount',
        readonly=False,
    )
    wt_percent = fields.Float(
        string='% Tax',
    )
    amount = fields.Float(
        string='Tax Amount',
        readonly=False,
    )
    ref_move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Ref Journal Item',
        help="Reference back to journal item which create wt move",
    )

    @api.onchange('wt_cert_income_type')
    def _onchange_wt_cert_income_type(self):
        if self.wt_cert_income_type:
            select_dict = dict(WHT_CERT_INCOME_TYPE)
            self.wt_cert_income_desc = select_dict[self.wt_cert_income_type]
        else:
            self.wt_cert_income_desc = False

    @api.onchange('wt_percent')
    def _onchange_wt_percent(self):
        if self.base:
            self.amount = self.base * self.wt_percent / 100
        if self.amount:
            if self.wt_percent:
                self.base = self.amount * 100 / self.wt_percent
            else:
                self.base = 0.0
