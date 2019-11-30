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
    total_duration_time = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Duration Time.'
    )
    total_used_time = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Used Time.'
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
            package_exp = package_line.filtered(
                lambda l: l.date_end < fields.Date.today())
            task_line_exp = \
                rec.task_line_ids.filtered(lambda l: not l.package_id)

            rec.total_effective_package = sum(package_line.mapped('effective'))
            rec.total_used_effective_package = \
                sum(rec.task_line_ids.mapped('unit_amount'))
            rec.balance = \
                rec.total_effective_package - rec.total_used_effective_package
            rec.total_effective_package = sum(package_line.mapped('effective'))
            rec.total_duration_time = sum(package_line.mapped('duration'))

            rec.total_used_time = sum(package_line.mapped('used_time_package'))
            for line in package_exp:
                rec.total_used_time += (line.duration - line.used_time_package)
            for task_line in task_line_exp:
                rec.total_used_time += task_line.unit_amount

    @api.multi
    def _compute_total_stage(self):
        for rec in self:
            rec.total_stage_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    self.task_id.stage_id.closed).mapped('unit_amount'))
            rec.total_stage_not_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    not self.task_id.stage_id.closed).mapped('unit_amount'))


class Task(models.Model):
    _inherit = 'project.task'

    expiry = fields.Boolean()
