from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_frontend_writable_fields(self):
        # La comuna (city_id) se elige desde el formulario de dirección del sitio.
        return super()._get_frontend_writable_fields() | {'city_id'}
