# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, _
from odoo.exceptions import ValidationError


class ReportProject(models.TransientModel):
    _name = 'report.project'
    _description = 'Wizard for report.project'
    _inherit = 'xlsx.report'

    # Search Criteria
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        readonly=True,
        default=lambda self: self._get_project(),
        help='project is selected',
    )
    state_id = fields.Many2one(
        'project.task.type',
        string='Stage',
        required=True,
        readonly=True,
        default=lambda self: self._get_stage_close(),
        help='closed is "True" in stage configuration',
    )

    # Report Result, project.task
    results = fields.Many2many(
        'project.task',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing stored in database',
    )
    # Report Result, project.support.package.line
    results_package = fields.Many2many(
        'project.support.package.line',
        string='Results Package',
        compute='_compute_results_package',
        help='Use compute fields, so there is nothing stored in database',
    )

    @api.model
    def _get_project(self):
        project_id = self._context.get('active_id')
        project = self.env['project.project'].search([('id', '=', project_id)])
        return project

    @api.model
    def _get_stage_close(self):
        stage = self.env['project.task.type'].search([('closed', '=', True)])
        if len(stage) > 1:
            raise ValidationError(_("Stage 'close' has more than 1, \
                Please configuration stage in project."))
        return stage

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['project.task']
        domain = [('project_id', '=', self.project_id.id),
                  ('stage_id', '=', self.state_id.id)]
        self.results = Result.search(domain)

    @api.multi
    def _compute_results_package(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['project.support.package.line']
        domain = [('project_id', '=', self.project_id.id)]
        self.results_package = Result.search(domain)
