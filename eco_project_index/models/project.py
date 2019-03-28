from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = 'project.project'

    project_index = fields.Boolean(
        'Index',
        default=False,
        help='config this project is index',
    )

    @api.constrains('project_index')
    def _check_constraint_index(self):
        if self.project_index:
            index_id = self.env['project.project'].search(
                [('project_index', '!=', False)]
                ).filtered(lambda l: l.id != self.id)
            if index_id:
                raise ValidationError(_("Other project is has already!"))
