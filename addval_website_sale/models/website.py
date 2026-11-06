from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    website_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta analítica Website',
    )
