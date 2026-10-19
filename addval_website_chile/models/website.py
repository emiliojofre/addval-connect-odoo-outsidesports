# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# Vistas que pertenecen a UN sitio (website_id) y deben seguir al sitio marcado.
# El flag JS (chile_b2c_flag) es generico y se decide con website.chile_b2c_enabled.
_SITE_VIEW_XMLIDS = (
    'address_chile_rut_phone',
    'chile_signup_form_b2c',
    'chile_confirmation_signup_text',
    'chile_shipping_delete_flag',
    'chile_shipping_delete_button',
    'outside_hide_pvp_catalog',
    'outside_hide_pvp_product',
)


class Website(models.Model):
    _inherit = 'website'

    chile_b2c_enabled = fields.Boolean(
        string='Aplicar ajustes Chile B2C',
        help='Activa en este sitio los ajustes B2C de Chile: precio con IVA '
             'incluido, RUT/teléfono/comuna en el checkout, registro de '
             'clientes y ocultar PVP. Solo un sitio puede tenerlo marcado.',
    )

    @api.constrains('chile_b2c_enabled')
    def _check_chile_b2c_unico(self):
        if self.search_count([('chile_b2c_enabled', '=', True)]) > 1:
            raise ValidationError(_(
                'Solo un sitio web puede tener marcado "Aplicar ajustes Chile B2C".'
            ))

    @api.model
    def _chile_b2c_site(self):
        return self.sudo().search([('chile_b2c_enabled', '=', True)], limit=1)

    @api.model
    def _chile_b2c_sync_views(self):
        """Deja las vistas por sitio del modulo ligadas al sitio marcado
        (por ID). Sin sitio marcado quedan inactivas, nunca globales."""
        imds = self.env['ir.model.data'].sudo().search([
            ('module', '=', 'addval_website_chile'),
            ('model', '=', 'ir.ui.view'),
            ('name', 'in', list(_SITE_VIEW_XMLIDS)),
        ])
        views = self.env['ir.ui.view'].sudo().with_context(active_test=False).browse(imds.mapped('res_id')).exists()
        site = self._chile_b2c_site()
        if site:
            views.write({'website_id': site.id, 'active': True})
        else:
            views.write({'active': False})

    def write(self, vals):
        res = super().write(vals)
        if 'chile_b2c_enabled' in vals:
            self.env['website']._chile_b2c_sync_views()
        return res
