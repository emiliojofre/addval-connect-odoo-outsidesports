from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.website_id')
    def _compute_analytic_distribution(self):
        """Líneas de pedidos web: 100 % en la cuenta analítica del sitio
        (como en 16, donde se sobrescribía en cada sale_get_order)."""
        super()._compute_analytic_distribution()
        for line in self:
            account = line.order_id.website_id.website_analytic_id
            if account and not line.display_type:
                line.analytic_distribution = {str(account.id): 100}
