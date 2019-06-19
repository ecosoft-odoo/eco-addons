from odoo import models, api, _


class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.

            ex: send email by subject = 'issue-nameproject : title'
                this project_id is nameproject
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        try:
            project_name = \
                msg.get('subject').split(':')[0].split('-')[1].strip()
            project_id = self.env['project.project'].search(
                [('name', '=', project_name.upper())]).id
        except IndexError:
            project_id = False
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id'),
            'project_id': project_id or 1
        }
        defaults.update(custom_values)

        task = super(Task, self.with_context(create_context)).message_new(
            msg, custom_values=defaults)
        email_list = task.email_split(msg)
        partner_ids = [p for p in task._find_partner_from_emails(
            email_list, force_create=False) if p]
        task.message_subscribe(partner_ids)
        return task
