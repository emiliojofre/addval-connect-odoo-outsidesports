# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): la comuna (city_id) del formulario de
# dirección rellena la ciudad, el código postal y la región antes de validar.
# En 19 el formulario lo procesan el portal (/my/address) y website_sale
# (/shop/address/submit), así que el mixin se aplica a ambos controladores.
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ChileCommuneAddressMixin:

    def _parse_form_data(self, form_data):
        address_values, extra_form_data = super()._parse_form_data(form_data)
        city_id = address_values.get('city_id')
        if city_id:
            city = request.env['res.city'].sudo().browse(city_id).exists()
            if city:
                address_values['city'] = city.name
                if not address_values.get('zip') and city.zipcode:
                    address_values['zip'] = city.zipcode
                if not address_values.get('state_id') and city.state_id:
                    address_values['state_id'] = city.state_id.id
                if not address_values.get('country_id') and city.country_id:
                    address_values['country_id'] = city.country_id.id
            else:
                address_values['city_id'] = False
        elif 'city_id' in address_values or address_values.get('city'):
            # País distinto de Chile (el selector va desactivado): sin comuna.
            address_values['city_id'] = False
        return address_values, extra_form_data


class CustomerPortalChileCommune(ChileCommuneAddressMixin, CustomerPortal):
    pass


class WebsiteSaleChileCommune(ChileCommuneAddressMixin, WebsiteSale):
    pass
