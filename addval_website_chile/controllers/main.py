# -*- coding: utf-8 -*-
# Port a Odoo 19 (Outside Sports): validaciones del formulario de dirección
# solo en el sitio B2C (id 3): teléfono chileno (+56 y 9 dígitos) y RUT
# obligatorio y válido en la dirección de facturación. En 19 el formulario lo
# procesan el portal y website_sale con _validate_address_values.
import re

from odoo import _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale

B2C_WEBSITE_ID = 3
PHONE_PATTERN = re.compile(r'^\+56\d{9}$')


def _is_b2c():
    website = getattr(request, 'website', None)
    return bool(website) and website.id == B2C_WEBSITE_ID


def _validar_rut(rut_raw):
    rut = rut_raw.strip().replace('.', '').replace(' ', '').upper()
    if '-' in rut:
        partes = rut.split('-')
        if len(partes) != 2:
            return False, rut_raw
        num_str, dv = partes
    elif len(rut) >= 2:
        num_str, dv = rut[:-1], rut[-1]
    else:
        return False, rut_raw
    if not num_str.isdigit():
        return False, rut_raw
    num = int(num_str)
    if num < 1000000 or num > 99999999:
        return False, rut_raw
    suma, multiplicador = 0, 2
    for d in reversed(num_str):
        suma += int(d) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    resto = 11 - (suma % 11)
    dv_esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    if dv != dv_esperado:
        return False, rut_raw
    return True, f"{num_str}-{dv_esperado}"


def _normalizar_telefono(phone_raw):
    phone = phone_raw.strip().replace(' ', '').replace('-', '')
    if re.match(r'^\+56\d{9}$', phone):
        return phone
    if re.match(r'^56\d{9}$', phone):
        return '+' + phone
    if re.match(r'^\d{9}$', phone):
        return '+56' + phone
    return phone_raw.strip()


class ChileB2CAddressMixin:

    def _validate_address_values(
        self, address_values, partner_sudo, address_type, use_delivery_as_billing,
        required_fields, **kwargs,
    ):
        if not _is_b2c():
            return super()._validate_address_values(
                address_values, partner_sudo, address_type, use_delivery_as_billing,
                required_fields, **kwargs,
            )
        phone_raw = (address_values.get('phone') or '').strip()
        if phone_raw:
            address_values['phone'] = _normalizar_telefono(phone_raw)
        vat_raw = (address_values.get('vat') or '').strip()
        if vat_raw:
            valido, vat_norm = _validar_rut(vat_raw)
            address_values['vat'] = vat_norm if valido else vat_raw

        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, partner_sudo, address_type, use_delivery_as_billing,
            required_fields, **kwargs,
        )

        phone = (address_values.get('phone') or '').strip()
        if phone and not PHONE_PATTERN.fullmatch(phone):
            invalid_fields.add('phone')
            msg = _("Teléfono inválido. Ingresa 9 dígitos, ej: 912345678.")
            if msg not in error_messages:
                error_messages.append(msg)

        if address_type == 'billing' or use_delivery_as_billing:
            vat = (address_values.get('vat') or '').strip()
            if not vat and 'vat' in address_values:
                missing_fields.add('vat')
                msg = _("El RUT es obligatorio.")
                if msg not in error_messages:
                    error_messages.append(msg)
            elif vat and not _validar_rut(vat)[0] and 'vat' not in invalid_fields:
                # En 19 base_vat ya valida el RUT chileno; solo se añade el
                # mensaje propio si la validación estándar no lo marcó.
                invalid_fields.add('vat')
                msg = _("RUT inválido. Verifica el dígito verificador. Ej: 12345678-9")
                if msg not in error_messages:
                    error_messages.append(msg)
        return invalid_fields, missing_fields, error_messages


class CustomerPortalChileB2C(ChileB2CAddressMixin, CustomerPortal):
    pass


class WebsiteSaleChileB2C(ChileB2CAddressMixin, WebsiteSale):
    pass
