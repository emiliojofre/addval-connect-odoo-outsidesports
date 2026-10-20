# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Estados posibles de Alas Express: color semáforo + descripción legible.
# Única fuente de verdad para ambos — antes vivían duplicados (un dict de
# colores acá y un dict de descripciones repetido a mano en el XML de la
# vista, que no reflejaba el estado real del picking, solo una leyenda fija).
ALAS_STATUS_INFO = {
    'Planificación': (0, 'Orden recibida por Alas (estado inicial)'),
    'Recepción Física': (3, 'Alas recogió las cajas en bodega'),
    'Entrega Agendada': (3, 'Alas contactó al destinatario'),
    'Entrega Reagendada': (3, 'Alas reagendó el contacto con el destinatario'),
    'Entrega Ruteada': (4, 'Ruta del día siguiente generada'),
    'En Ruta': (10, 'Mensajero en camino'),
    'Entregado': (10, 'Entrega exitosa ✅'),
    'Rechazado Agendamiento': (1, 'Destinatario rechazó en contacto ❌'),
    'Rechazado Terreno': (1, 'Rechazado en el domicilio ❌'),
    'No Entregable': (1, '3 intentos fallidos ❌'),
    'Rechazada B2B': (1, 'Orden rechazada manualmente desde Odoo ❌'),
}


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ── Campo auxiliar para visibilidad en vistas (attrs no acepta x.y en Odoo 16) ──
    alas_is_carrier = fields.Boolean(
        string='Es Alas Express',
        compute='_compute_alas_is_carrier',
        store=False,
    )

    @api.depends('carrier_id', 'carrier_id.delivery_type')
    def _compute_alas_is_carrier(self):
        for rec in self:
            rec.alas_is_carrier = rec.carrier_id.delivery_type == 'alas_express'

    # ── Campos Alas Express ──────────────────────────────────────────────────
    alas_delivery_order_id = fields.Char(
        string='ID Alas Express',
        copy=False,
        readonly=True,
        help='Identificador de la Delivery Order asignado por Alas Express.',
    )
    alas_labels_url = fields.Char(
        string='URL Etiquetas Alas',
        copy=False,
        readonly=True,
    )
    alas_package_codes = fields.Char(
        string='Códigos de Paquetes Alas',
        copy=False,
        readonly=True,
        help='Lista de códigos de paquetes asociados a la orden en Alas Express.',
    )
    alas_status = fields.Char(
        string='Estado Alas Express',
        copy=False,
        readonly=True,
        help='Último estado sincronizado desde Alas Express.',
    )
    alas_delivery_expected = fields.Datetime(
        string='Entrega Estimada Alas',
        copy=False,
        readonly=True,
    )
    alas_status_color = fields.Integer(
        string='Color Estado',
        compute='_compute_alas_status_color',
        store=False,
    )
    alas_status_description = fields.Char(
        string='Descripción Estado Alas',
        compute='_compute_alas_status_description',
        store=False,
        help='Descripción legible del estado ACTUAL de este envío (alas_status), '
             'no una leyenda fija — antes la vista solo mostraba una tabla de '
             'referencia estática que no reflejaba el dato real del picking.',
    )

    # ── Computados ───────────────────────────────────────────────────────────

    @api.depends('alas_status')
    def _compute_alas_status_color(self):
        """Asigna un color semáforo según el estado de Alas."""
        for rec in self:
            info = ALAS_STATUS_INFO.get(rec.alas_status)
            rec.alas_status_color = info[0] if info else 0

    @api.depends('alas_status')
    def _compute_alas_status_description(self):
        """Descripción legible del estado ACTUAL (no una leyenda fija)."""
        for rec in self:
            info = ALAS_STATUS_INFO.get(rec.alas_status)
            if info:
                rec.alas_status_description = info[1]
            elif rec.alas_status:
                rec.alas_status_description = _('Estado no reconocido — revisar con Alas Express.')
            else:
                rec.alas_status_description = ''

    # ── Acciones desde el picking ────────────────────────────────────────────

    def action_alas_send_order(self):
        """Crea la Delivery Order en Alas Express desde el picking."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_(
                'El método de envío del albarán "%s" no es Alas Express.'
            ) % self.name)
        if self.alas_delivery_order_id:
            raise UserError(_(
                'Este albarán ya tiene una orden en Alas Express (ID: %s).\n'
                'Para crear una nueva, primero rechace la actual.'
            ) % self.alas_delivery_order_id)

        carrier.alas_create_delivery_order(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main',
        }

    def action_alas_get_status(self):
        """Actualiza el estado de la orden desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_status(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main',
        }

    def action_alas_get_label(self):
        """Obtiene/regenera la etiqueta PDF desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_label(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Etiqueta Alas Express'),
                'message': _('Etiqueta generada y guardada como adjunto del albarán.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_alas_get_label_zpl(self):
        """Obtiene la etiqueta en formato ZPL desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_label_zpl(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Etiqueta ZPL Alas Express'),
                'message': _('Etiqueta ZPL guardada como adjunto del albarán.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_alas_reject_order(self):
        """Rechaza la Delivery Order en Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_reject_order(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alas Express'),
                'message': _('Orden rechazada. Estado: %s') % self.alas_status,
                'type': 'warning',
                'sticky': False,
            },
        }

    def action_alas_open_label_attachment(self):
        """Abre el adjunto de la etiqueta PDF del picking, descargándolo si no existe."""
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('name', 'like', 'alas_label_'),
        ], order='create_date desc', limit=1)

        # Si no existe adjunto, intentar descargarlo ahora
        if not attachment:
            self.carrier_id.alas_get_label(self)
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', 'stock.picking'),
                ('res_id', '=', self.id),
                ('name', 'like', 'alas_label_'),
            ], order='create_date desc', limit=1)

        if not attachment:
            raise UserError(_('No se pudo obtener la etiqueta de Alas Express.'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    # ── Cron / Actualización masiva de estado ────────────────────────────────

    def cron_alas_update_status(self):
        """
        Cron para actualizar el estado de todos los pickings con Alas Express
        que no estén en estado final EN ALAS.

        OJO: el filtro NO debe mirar el estado interno de bodega
        (stock.picking.state = done/cancel) — ese estado indica que Odoo
        completó su propia operación de despacho (que ocurre casi de
        inmediato al crear la orden en Alas), no que Alas terminó de
        entregar. Filtrar por él excluía de este cron prácticamente todos
        los pickings reales, dejando alas_status congelado para siempre en
        el valor inicial "Planificación" (confirmado en producción: 0
        pickings procesados en cada corrida durante semanas). El criterio
        correcto es si el envío en ALAS sigue activo (alas_status no es un
        estado final de Alas); solo se excluyen los pickings cancelados en
        Odoo, que ya no tiene sentido seguir rastreando.
        """
        FINAL_STATES = {'Entregado', 'Rechazado Agendamiento', 'Rechazado Terreno', 'No Entregable', 'Rechazada B2B'}
        pickings = self.search([
            ('carrier_id.delivery_type', '=', 'alas_express'),
            ('alas_delivery_order_id', '!=', False),
            ('alas_status', 'not in', list(FINAL_STATES)),
            ('state', '!=', 'cancel'),
        ])
        _logger.info('Alas Express cron: actualizando %d pickings', len(pickings))
        for picking in pickings:
            try:
                picking.carrier_id.alas_get_status(picking)
            except Exception as e:
                _logger.warning('Alas Express cron: error en picking %s → %s', picking.name, e)
