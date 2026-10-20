from odoo import fields, models


class ProductWebsiteLabel(models.Model):
    _name = 'product.website.label'
    _description = 'Label de producto por sitio web'
    _order = 'product_tmpl_id, website_id'

    product_tmpl_id = fields.Many2one(
        'product.template', string='Producto', required=True,
        ondelete='cascade', index=True)
    website_id = fields.Many2one(
        'website', string='Sitio web', required=True, ondelete='cascade')
    label_id = fields.Many2one(
        'website.product.label', string='Label', ondelete='set null',
        help='Dejar vacío para no mostrar ninguna label en este sitio.')
    lbl_title = fields.Text(
        string='Texto de la label',
        help='Solo para labels de tipo "Custom Ribbons". '
             'Si se deja vacío se usa el texto general del producto.')

    _sql_constraints = [
        ('product_website_uniq', 'unique(product_tmpl_id, website_id)',
         'Este producto ya tiene una label definida para ese sitio web.'),
    ]
