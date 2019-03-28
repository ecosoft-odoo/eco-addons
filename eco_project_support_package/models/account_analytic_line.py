# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
<<<<<<< HEAD
<<<<<<< HEAD
    _order = 'task_id, date desc'
=======
    _order = 'task_id, date'
>>>>>>> 51ba9b5... [FIX] order by task_id and date in timesheet_ids
=======
    _order = 'task_id, package_id, date desc'

    package_id = fields.Many2one(
        'project.support.package.line',
        required=True,
        domain=lambda self: self._domain_package_id(),
        default=lambda self: self._default_package_id(),
    )

    def _default_package_id(self):
        package_line = self.env['project.support.package.line'].search([
            ('project_id', '=', self._context.get('default_project_id', False))
        ]).filtered(lambda l: l.date_end >= fields.Date.today())
        if package_line:
            return package_line[0]

    def _domain_package_id(self):
        return [
            ('project_id', '=', self._context.get('default_project_id', False))
        ]
>>>>>>> 2dd2d86... [FIX] clean code and project_support
