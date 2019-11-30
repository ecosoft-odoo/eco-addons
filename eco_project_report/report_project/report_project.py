# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, _
from odoo.exceptions import ValidationError


class ReportProjectView(models.TransientModel):
    _name = 'report.project.view'
    _description = 'Report Project View'
    _inherit = 'project.task'
    _order = 'id'

    package_name = fields.Char()


class ReportPackageView(models.TransientModel):
    _name = 'report.package.view'
    _description = 'Report Package View'
    _inherit = 'project.support.package.line'
    _order = 'id'

    used_time_package_exp = fields.Float(compute='_compute_used_time_exp')
    package_id = fields.Integer()

    def _compute_used_time_exp(self):
        for rec in self:
            task_line = rec.env['account.analytic.line']
            line_package_exp = task_line.search([
                ('project_id', '=', rec.project_id.id),
                ('package_id', '=', False)])
            used_time_package = task_line.search([
                ('project_id', '=', rec.project_id.id),
                ('package_id', '=', rec.package_id)])
            rec.used_time_package_exp = \
                sum(used_time_package.mapped('unit_amount'))
            for line in line_package_exp:
                if rec.duration and rec.date_end < line.date:
                    rec.used_time_package_exp += line.unit_amount


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
    # Result sheet 1
    results_package = fields.Many2many(
        comodel_name='report.package.view',
        string='Results Package',
        compute='_compute_results_package',
        help='Use compute fields, so there is nothing stored in database',
    )
    # Result sheet 2
    results = fields.Many2many(
        comodel_name='report.project.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing stored in database',
    )
    # Result sheet 3
    results_inprogress = fields.Many2many(
        comodel_name='project.task',
        string='Results In-Progress',
        compute='_compute_results_inprogress',
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

    def _get_used_time_exp_package(self, line):
        package = self.project_id.support_package_line_ids.filtered(
            lambda l: l.id == line.get('id'))
        balance = package.duration - package.used_time_package
        return balance

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        self._cr.execute("""
            SELECT pt.*, string_agg(distinct pspl.name, ',') as package_name
            FROM project_task pt
            JOIN account_analytic_line aal ON aal.task_id = pt.id
            LEFT JOIN project_support_package_line pspl
            ON pspl.id = aal.package_id
            WHERE pt.project_id = %s and pt.stage_id = %s
            GROUP BY pt.id
            ORDER BY pt.code
        """, (self.project_id.id, self.state_id.id))

        results = self._cr.dictfetchall()
        ReportLine = self.env['report.project.view']
        for line in results:
            self.results += ReportLine.new(line)

    @api.multi
    def _compute_results_package(self):
        self.ensure_one()
        self._cr.execute("""
            SELECT *, id as package_id
            FROM project_support_package_line
            WHERE project_id = %s
        """ % (self.project_id.id))

        results = self._cr.dictfetchall()
        ReportLine = self.env['report.package.view']
        for line in results:
            self.results_package += ReportLine.new(line)
            # expired
            if line.get('date_end', False) < fields.Date.today():
                self.results_package += ReportLine.new(
                    {'date_start': line.get('date_end', False),
                     'date_end': line.get('date_end', False),
                     'name': 'Expiration',
                     'used_time_package_exp':
                        self._get_used_time_exp_package(line)})

    @api.multi
    def _compute_results_inprogress(self):
        self.ensure_one()
        # find stage not in 'Done' and 'Cancelled'
        stage = self.env['project.task.type'].search([('fold', '=', False)])
        Result = self.env['project.task']
        domain = [('project_id', '=', self.project_id.id),
                  ('stage_id', '=', stage.ids)]
        self.results_inprogress = Result.search(domain)
