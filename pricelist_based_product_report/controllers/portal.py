from odoo import http
from odoo.http import content_disposition, request


class PricelistReportPortal(http.Controller):

    # Port 19: auth='user' (en 16 era 'public' y cualquiera podía descargar
    # el catálogo con stock y precios sin iniciar sesión).
    @http.route(['/my/pricelist_report/csv'], type='http', auth="user", website=True)
    def portal_pricelist_report(self, **kwargs):
        report = request.env['pricelist.based.product.report.wizard'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
        }).generate_report_from_website()
        content = (report.json_file or '').encode('utf-8')
        headers = [
            ('Content-Type', 'text/csv; charset=utf-8'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition(report.filename)),
        ]
        return request.make_response(content, headers=headers)
