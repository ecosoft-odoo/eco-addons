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
<<<<<<< HEAD
    total_man_hour = fields.Float(
<<<<<<< HEAD
        'Total Support Package',
=======
        'Total Man-Hour',
>>>>>>> 18d7f30... [ENH] module eco_project_support_package
=======
    total_duration_package = fields.Float(
>>>>>>> 126efcb... [ADD] package available and effective
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour in Support Package.'
    )
    used_man_hour = fields.Float(
<<<<<<< HEAD
        'Total used Man-Hour',
=======
        'Used Man-Hour',
>>>>>>> 18d7f30... [ENH] module eco_project_support_package
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
    total_available_package = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour available in Support Package.'
    )
    total_effective_package = fields.Float(
        compute='_compute_man_hour',
        readonly=True,
        help='Total Man-Hour effective in Support Package.'
    )
>>>>>>> 126efcb... [ADD] package available and effective
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
=======
>>>>>>> 18d7f30... [ENH] module eco_project_support_package

    @api.multi
    def _compute_man_hour(self):
        for rec in self:
            package_not_expiry = rec.support_package_line_ids.filtered(
                lambda l: l.date_end >= fields.Date.today())
            duration_not_expiry = [
                x.duration for x in package_not_expiry if not x.effective]
            effective_time = sum(rec.support_package_line_ids.filtered(
                lambda l: l.date_end >= fields.Date.today()
                ).mapped('effective'))
            rec.total_duration_package = \
                sum(rec.support_package_line_ids.mapped('duration'))
            rec.used_man_hour = sum(rec.task_line_ids.mapped('unit_amount'))
<<<<<<< HEAD
            rec.balance_man_hour = rec.total_man_hour - rec.used_man_hour
<<<<<<< HEAD
=======
            rec.balance_man_hour = \
                rec.total_duration_package - rec.used_man_hour
            rec.total_available_package = effective_time + \
                sum(duration_not_expiry)
            rec.total_effective_package = \
                sum(rec.support_package_line_ids.mapped('effective'))
>>>>>>> 126efcb... [ADD] package available and effective

    @api.multi
    def _compute_total_stage(self):
        for rec in self:
            rec.total_stage_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    self.task_id.stage_id.closed).mapped('unit_amount'))
            rec.total_stage_not_close = \
                sum(rec.task_line_ids.filtered(lambda self:
                    not self.task_id.stage_id.closed).mapped('unit_amount'))
=======
>>>>>>> 18d7f30... [ENH] module eco_project_support_package
