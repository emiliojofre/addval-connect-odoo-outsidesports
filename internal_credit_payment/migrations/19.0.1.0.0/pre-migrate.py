# Upgrade 16 -> 19 (Outside Sports): el XML de 16 creaba el proveedor de pago,
# el producto "Credit Product" y el diario "Credit Bank" sin noupdate. Como el
# XML de 19 ya no los declara, Odoo los borraría al final de la actualización
# (_process_end). El proveedor tiene cientos de transacciones: se marcan como
# noupdate para conservarlos.
import logging

_logger = logging.getLogger(__name__)

KEEP = ('payment_provider_credit', 'product_product_299', 'product_product_299_product_template',
        'credit_account_journal')


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data SET noupdate = TRUE
         WHERE module = 'internal_credit_payment'
           AND (name IN %s OR model IN ('payment.provider', 'product.product', 'product.template',
                                        'account.journal'))
     RETURNING model, name
    """, [KEEP])
    _logger.info("upgrade19 internal_credit_payment: conservados %s", cr.fetchall())
