from odoo import models


class WebsiteProductLabel(models.Model):
    _inherit = 'website.product.label'

    def _wpl_rotation(self, mode, value):
        if mode == 'rt_left':
            return 'transform:rotate(-%sdeg);' % (value or '0')
        if mode == 'rt_right':
            return 'transform:rotate(%sdeg);' % (value or '0')
        return ''

    def get_wpl_image_style(self):
        """Mismo estilo inline que generan las plantillas de BrowseInfo."""
        self.ensure_one()
        return (
            'height:%spx;width:%spx;margin-left:%spx;margin-right:%spx;'
            'margin-top:%spx;margin-bottom:%spx;' % (
                self.height or '0', self.width or '0',
                self.margin_left or '0', self.margin_right or '0',
                self.margin_top or '0', self.margin_bottom or '0')
            + self._wpl_rotation(self.rotate_label, self.rotate_value))

    def get_wpl_font_style(self):
        self.ensure_one()
        return (
            'padding:5px 15px;font-weight:bold;position:absolute;color:%s;'
            'font-size:%spx;left:%spx;right:%spx;top:%spx;bottom:%spx;' % (
                self.font_color or 'none', self.font_size or '15',
                self.font_left or '0', self.font_right or '0',
                self.font_top or '0', self.font_bottom or '0')
            + self._wpl_rotation(self.font_rotate_label, self.font_rotate_value))
