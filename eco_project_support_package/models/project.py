# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    task_line_ids = fields.One2many(
        'account.analytic.line',
        'project_id',
        readonly=True,
        help='Get all task in this project.'
    )

    support_package_line_ids = fields.One2many(
        'project.support.package.line',
        'project_id',
        help='Add Support Package Man-Hour.'
    )
    total_effective_package = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour available in Support Package.'
    )
    total_used_effective_package = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Used available Man-Hour.'
    )
    total_package_not_exp = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Support Man-Hour. (Not Expiry)'
    )
    total_used_not_exp = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Used Man-Hour. (Not Expiry)'
    )
    balance = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Balance Total Man-Hour - Total Used Man-Hour'
    )
    total_effective_package = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour effective in Support Package.'
    )
    total_stage_close = fields.Float(
        'Total Task Close',
        compute='_compute_total_stage',
        readonly=True,
        help='Total Man-Hour in stage close',
    )
    total_stage_not_close = fields.Float(
        'Total Task InProgress',
        compute='_compute_total_stage',
        readonly=True,
        help='Total Man-Hour in stage not close',
    )

    @api.multi
    def _compute_man_hour(self):
        for rec in self:
            package_line = rec.support_package_line_ids
            rec.total_effective_package = sum(package_line.mapped('effective'))
            rec.total_used_effective_package = \
                sum(rec.task_line_ids.mapped('unit_amount'))
            rec.balance = \
                rec.total_effective_package - rec.total_used_effective_package
            rec.total_effective_package = sum(package_line.mapped('effective'))
            rec.total_package_not_exp = sum(package_line.filtered(
                lambda l: l.date_end >= fields.Date.today()
            ).mapped('duration'))
            rec.total_used_not_exp = sum(package_line.filtered(
                lambda l: l.date_end >= fields.Date.today()
            ).mapped('used_time_package'))

    @api.multi
    def _compute_total_stage(self):
        for rec in self:
            rec.total_stage_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    self.task_id.stage_id.closed).mapped('unit_amount'))
            rec.total_stage_not_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    not self.task_id.stage_id.closed).mapped('unit_amount'))
