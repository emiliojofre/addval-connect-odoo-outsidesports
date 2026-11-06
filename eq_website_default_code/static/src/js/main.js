/** @odoo-module **/
// Port a Odoo 19 (Outside Sports): actualiza SKU y PVP al cambiar de variante.

import { patch } from '@web/core/utils/patch';
import { WebsiteSale } from '@website_sale/interactions/website_sale';

patch(WebsiteSale.prototype, {
    _onChangeCombination(ev, parent, combination) {
        super._onChangeCombination(...arguments);
        const defaultCodeEl = parent.querySelector('.default_code');
        if (defaultCodeEl) {
            defaultCodeEl.textContent = combination.default_code || '';
        }
        const pvpEl = parent.querySelector('.pvp');
        if (pvpEl) {
            pvpEl.textContent = combination.pvp
                ? new Intl.NumberFormat('de-DE').format(combination.pvp)
                : '';
        }
    },
});
