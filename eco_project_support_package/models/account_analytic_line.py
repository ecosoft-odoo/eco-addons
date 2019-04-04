# -*- coding: utf-8 -*-

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'task_id, date'
