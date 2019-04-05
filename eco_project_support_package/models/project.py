# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

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
    total_man_hour = fields.Float(
        'Total Support Package',
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour in Support Package.'
    )
    used_man_hour = fields.Float(
        'Total used Man-Hour',
        compute='_compute_man_hour',
        readonly=True,
        help='Total Used Man-Hour.'
    )
    balance_man_hour = fields.Float(
        'Balance',
        compute='_compute_man_hour',
        readonly=True,
        help='Balance Total Man-Hour - Total Used Man-Hour'
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
            rec.total_man_hour = \
                sum(rec.support_package_line_ids.mapped('duration'))
            rec.used_man_hour = sum(rec.task_line_ids.mapped('unit_amount'))
            rec.balance_man_hour = rec.total_man_hour - rec.used_man_hour

    @api.multi
    def _compute_total_stage(self):
        for rec in self:
            rec.total_stage_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    self.task_id.stage_id.closed).mapped('unit_amount'))
            rec.total_stage_not_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    not self.task_id.stage_id.closed).mapped('unit_amount'))
