# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Crea la columna y marca el sitio que hoy tiene las vistas del modulo
    (por ID, sin depender del nombre del sitio)."""
    cr.execute("ALTER TABLE website ADD COLUMN IF NOT EXISTS chile_b2c_enabled boolean")
    cr.execute("""
        SELECT DISTINCT v.website_id
          FROM ir_ui_view v
          JOIN ir_model_data d ON d.model = 'ir.ui.view' AND d.res_id = v.id
         WHERE d.module = 'addval_website_chile' AND v.website_id IS NOT NULL
    """)
    ids = [r[0] for r in cr.fetchall()]
    if len(ids) == 1:
        cr.execute("UPDATE website SET chile_b2c_enabled = (id = %s)", (ids[0],))
