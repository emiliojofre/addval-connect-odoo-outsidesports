/** @odoo-module **/
// Port a Odoo 19 (Outside Sports): selector de comuna para Chile en el
// formulario de dirección estándar (checkout y Mi cuenta).
// - Filtra las comunas por la región elegida.
// - Copia el nombre de la comuna al campo oculto "city" (obligatorio en Odoo).
// - Si el país no es Chile, muestra el campo de texto de ciudad y desactiva el
//   selector (un <select> desactivado no se envía).

function setupWrapper(wrapper) {
    const form = wrapper.closest('form');
    if (!form || wrapper.dataset.clReady) {
        return;
    }
    wrapper.dataset.clReady = '1';
    const select = wrapper.querySelector('.o_cl_city_select');
    const input = wrapper.querySelector('.o_cl_city_input');
    const labelComuna = wrapper.querySelector('.o_cl_city_label_comuna');
    const labelCity = wrapper.querySelector('.o_cl_city_label_city');
    const chileId = wrapper.dataset.clCountryId;
    const countrySelect = form.querySelector('select[name="country_id"]');
    const stateSelect = form.querySelector('select[name="state_id"]');
    const zipInput = form.querySelector('input[name="zip"]');

    const isChile = () => countrySelect && chileId && countrySelect.value === chileId;

    const filterByState = () => {
        const stateId = stateSelect ? stateSelect.value : '';
        for (const option of select.options) {
            if (!option.value) {
                continue;
            }
            const visible = !stateId || option.dataset.stateId === stateId;
            option.hidden = !visible;
            option.disabled = !visible;
        }
        const current = select.selectedOptions[0];
        if (current && current.value && current.disabled) {
            select.value = '';
        }
    };

    const syncCity = () => {
        const current = select.selectedOptions[0];
        if (current && current.value) {
            input.value = current.textContent.trim();
            if (zipInput && !zipInput.value && current.dataset.zip) {
                zipInput.value = current.dataset.zip;
            }
            if (stateSelect && !stateSelect.value && current.dataset.stateId) {
                stateSelect.value = current.dataset.stateId;
            }
        } else if (isChile()) {
            input.value = '';
        }
    };

    const applyCountry = () => {
        const chile = isChile();
        select.style.display = chile ? '' : 'none';
        select.disabled = !chile;
        input.style.display = chile ? 'none' : '';
        if (labelComuna) {
            labelComuna.style.display = chile ? '' : 'none';
        }
        if (labelCity) {
            labelCity.style.display = chile ? 'none' : '';
        }
        if (chile) {
            filterByState();
            syncCity();
        }
    };

    select.addEventListener('change', syncCity);
    if (stateSelect) {
        stateSelect.addEventListener('change', () => {
            filterByState();
            syncCity();
        });
    }
    if (countrySelect) {
        // El JS estándar recarga regiones al cambiar de país; se espera a que termine.
        countrySelect.addEventListener('change', () => setTimeout(applyCountry, 400));
    }
    applyCountry();
}

function setupAll() {
    document.querySelectorAll('.o_cl_city_wrapper').forEach(setupWrapper);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAll);
} else {
    setupAll();
}