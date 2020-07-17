# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    def update_date_end(self, stage_id):
        task_type = self.env['project.task.type']
        stage = task_type.browse(stage_id)
        if stage.closed:
            return {'date_end': fields.Datetime.now()}
        return super().update_date_end(stage_id)
