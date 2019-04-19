# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class ProjectSupportPackageLine(models.Model):
    _name = 'project.support.package.line'
    _description = 'Project Support Package Line'

    project_id = fields.Many2one(
        'project.project',
        'Support Package',
    )
    date_start = fields.Date(
        'Start Date',
        required=True,
        help='date of buy support package',
    )
    date_end = fields.Date(
        'Expiry Date',
        help='Expiry date 1 year from Start Date',
    )
    ref = fields.Char(
        'Ref',
        help='Reference number invoice',
    )
    name = fields.Char(
        'Description',
        help='Description about Support Package',
    )
    duration = fields.Float(
        'Duration (hours)',
        help='Package Man-Hour'
    )

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.date_end = self.date_start + relativedelta(years=1)
