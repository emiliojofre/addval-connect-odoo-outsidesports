# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : <https://store.webkul.com/license.html/>
#################################################################################
# Port a Odoo 19 (Outside Sports):
# - Ya no se redefine /shop: el filtro de marca entra por sale_product_domain
#   (models/website_product_brand.py) y aquí solo se añaden valores al contexto
#   y el parámetro attrib_brand a los enlaces (keep).
# - La página propia de productos por marca (/product/brand/<id>) redirige a
#   /shop filtrado por esa marca, que en 19 ya tiene paginación, orden y filtros.
from werkzeug.urls import url_encode

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL


class WebsiteSaleBrands(WebsiteSale):

    def _wk_brand_set(self):
        return request.env['website']._get_wk_brand_set()

    def _shop_get_query_url_kwargs(self, search, min_price, max_price, order=None, tags=None, **kwargs):
        res = super()._shop_get_query_url_kwargs(
            search, min_price, max_price, order=order, tags=tags, **kwargs)
        attrib_brand = request.httprequest.args.getlist('attrib_brand')
        if attrib_brand:
            res['attrib_brand'] = attrib_brand
        return res

    def _get_additional_shop_values(self, values, **kwargs):
        res = super()._get_additional_shop_values(values, **kwargs)
        brand_set = self._wk_brand_set()
        Brand = request.env['wk.product.brand']
        res.update({
            'brand_set': brand_set,
            'brand_rec': Brand.search([
                ('website_published', '=', True),
                ('website_id', 'in', [request.website.id, False]),
            ]),
            'wk_brands': Brand.browse(brand_set),
        })
        return res

    @http.route([
        '/shop/brand/<model("wk.product.brand"):wk_brand>',
        '/shop/brand/<model("wk.product.brand"):wk_brand>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=False)
    def wk_shop_brand(self, wk_brand, page=0, **post):
        return request.redirect('/shop?%s' % url_encode({'attrib_brand': '%s-%s' % (wk_brand.id, wk_brand.id)}), code=301)

    @http.route([
        '/product/brand/<int:brand>',
        '/product/brand/<int:brand>/category/<model("product.public.category"):category>',
        '/product/brand/<int:brand>/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=False)
    def wk_product_brand(self, brand=False, category=None, page=0, **post):
        path = self._get_shop_path(category) if category else '/shop'
        return request.redirect('%s?%s' % (path, url_encode({'attrib_brand': '%s-%s' % (brand, brand)})), code=301)

    def _get_brand_search_domain(self, search):
        domain = [("website_published", "=", True), ('website_id', 'in', [request.website.id, False])]
        if search:
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]
        return domain

    @http.route(['/shop/brands', '/shop/brands/page/<int:page>'], type='http', auth="public", website=True)
    def wk_brands_page(self, page=0, search='', ppg=False, **post):
        try:
            ppg = int(ppg) if ppg else 0
        except ValueError:
            ppg = 0
        if not ppg:
            ppg = request.website.shop_ppg or 20
        url = "/shop/brands"
        if search:
            post["search"] = search
        keep = QueryURL('/shop/brands', search=search)
        brands = request.env['wk.product.brand'].search(self._get_brand_search_domain(search))
        pager = request.website.pager(url=url, total=len(brands), page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        values = {
            'search': search,
            'pager': pager,
            'wk_brands_list': brands[offset:offset + ppg],
            'search_count': len(brands),
            'ppg': ppg,
            'ppr': request.website.shop_ppr or 4,
            'keep': keep,
        }
        return request.render("website_product_brands.wk_brands_page", values)
