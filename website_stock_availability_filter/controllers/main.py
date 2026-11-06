# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
# Port a Odoo 19 (Outside Sports): se usan los hooks estándar en lugar de
# redefinir la ruta /shop.

from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class BizopleWebsiteSale(WebsiteSale):

    def _get_search_options(self, category=None, attribute_value_dict=None, tags=None,
                            min_price=0.0, max_price=0.0, conversion_rate=1, **post):
        res = super()._get_search_options(
            category=category, attribute_value_dict=attribute_value_dict, tags=tags,
            min_price=min_price, max_price=max_price, conversion_rate=conversion_rate, **post
        )
        res['show_instock'] = post.get('show_instock', False)
        return res

    def _shop_get_query_url_kwargs(self, search, min_price, max_price, order=None, tags=None, **kwargs):
        res = super()._shop_get_query_url_kwargs(
            search, min_price, max_price, order=order, tags=tags, **kwargs
        )
        res['show_instock'] = kwargs.get('show_instock')
        return res

    def _get_additional_shop_values(self, values, **kwargs):
        res = super()._get_additional_shop_values(values, **kwargs)
        res['show_instock'] = request.params.get('show_instock', False)
        return res
