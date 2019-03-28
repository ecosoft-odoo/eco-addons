# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class ProjectSupportPackageLine(models.Model):
    _name = 'project.support.package.line'
    _description = 'Project Support Package Line'

    project_id = fields.Many2one(
        'project.project',
        string='Support Package',
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        help='date of buy support package',
    )
    date_end = fields.Date(
        string='Expiry Date',
        help='Expiry date 1 year from Start Date',
    )
    ref = fields.Char(
        string='Ref',
        help='Reference number invoice',
    )
    name = fields.Char(
        string='Description',
        help='Description about Support Package',
    )
    duration = fields.Float(
        string='Duration (hours)',
        help='Package Man-Hour'
    )
    effective = fields.Float(
        string='Effective (hours)',
        compute='_compute_effective',
        readonly=True,
        help='Package effective Man-Hour'
    )

    def _compute_effective(self):
        for rec in self:
            timesheet_hours = sum(rec.env['account.analytic.line'].search([
                ('project_id', '=', rec.project_id.id),
                ('package_id', '=', rec.id)]).mapped('unit_amount'))
            rec.effective = timesheet_hours

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.date_end = self.date_start + relativedelta(years=1)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]
        package = self.search(domain + args, limit=limit)
        return package.name_get()

    @api.multi
    def name_get(self):
        """Return special label when showing fields in support package line"""
        res = []
        for record in self:
            timesheet_hours = sum(self.env['account.analytic.line'].search([
                ('project_id', '=', record.project_id.id),
                ('package_id', '=', record.id)]).mapped('unit_amount'))
            res.append((record.id, "%s (%s/%s)" % (
                record.name, timesheet_hours, record.duration)))
        return res
