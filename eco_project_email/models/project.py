# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields


class Project(models.Model):
    _inherit = 'project.project'

    email_cc = fields.Char()

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        support_template_id = \
            self.env.ref('eco_project_email.email_support_template').id
        if self.balance < 0.0:
            support_template_id = self.env.ref(
                'eco_project_email.email_support_expiry_template').id
        compose_form_id = \
            self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,
            default_model='project.project',
            default_use_template=bool(support_template_id),
            default_template_id=support_template_id,
            custom_layout='mail.mail_notification_light',
            default_email_cc=self.email_cc,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
