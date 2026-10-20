from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_label_ids = fields.One2many(
        'product.website.label', 'product_tmpl_id',
        string='Labels por sitio web', copy=True)

    def get_website_label_data(self, website=None):
        """Devuelve (label, texto) a mostrar en el sitio web dado.

        Si el producto tiene una línea para ese sitio, manda esa línea
        (con label vacía = sin label). Si no, se usa la label general.
        """
        self.ensure_one()
        website = website or self.env['website'].get_current_website()
        line = self.sudo().website_label_ids.filtered(
            lambda l: l.website_id == website)[:1]
        if line:
            return line.label_id, line.lbl_title or self.lbl_title or ''
        return self.sudo().select_label, self.lbl_title or ''
