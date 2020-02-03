# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def _send(self, auto_commit=False, raise_exception=False,
              smtp_session=None):
        for mail_id in self.ids:
            mail = self.browse(mail_id)
            mail.email_cc = self._context.get('default_email_cc', False)
        return super()._send(auto_commit, raise_exception, smtp_session)
