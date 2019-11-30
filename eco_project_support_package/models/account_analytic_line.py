from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'task_id, package_id, date desc'

    package_id = fields.Many2one(
        'project.support.package.line',
        domain=lambda self: self._domain_package_id(),
        default=lambda self: self._default_package_id(),
    )
    has_expiry = fields.Boolean(
        related='task_id.expiry',
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
