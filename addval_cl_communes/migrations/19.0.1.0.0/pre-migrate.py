# Upgrade 16 -> 19 (Outside Sports): este módulo hace obligatorio res.city.code,
# pero en producción hay algunas ciudades extranjeras creadas sin código (ya en
# 16). Al cargar el modelo Odoo intenta poner NOT NULL en la columna y deja un
# ERROR en el log ("column code of relation res_city contains null values"),
# que marca el build de Odoo.sh como fallido. Se les asigna un código antes:
# código ISO del país + id (p. ej. ES123), con el mismo estilo que CL16104.
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("""
        UPDATE res_city city
           SET code = COALESCE(country.code, 'XX') || city.id
          FROM res_city city2
     LEFT JOIN res_country country ON country.id = city2.country_id
         WHERE city2.id = city.id
           AND (city.code IS NULL OR city.code = '')
     RETURNING city.id, city.code
    """)
    _logger.info("upgrade19 addval_cl_communes: ciudades sin código -> %s", cr.fetchall())
