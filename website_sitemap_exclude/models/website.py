from odoo import models

PARAM_PREFIXES = 'website_sitemap_exclude.prefixes'


class Website(models.Model):
    _inherit = 'website'

    def _get_sitemap_excluded_prefixes(self):
        """Prefijos de path que no se publican en el sitemap."""
        value = self.env['ir.config_parameter'].sudo().get_param(PARAM_PREFIXES, '')
        return tuple(p.strip() for p in value.split(',') if p.strip())

    def _enumerate_pages(self, query_string=None, force=False):
        excluded = self._get_sitemap_excluded_prefixes()
        for page in super()._enumerate_pages(query_string=query_string, force=force):
            if not excluded or not page['loc'].startswith(excluded):
                yield page
