import { PaymentPostProcessing } from '@payment/interactions/post_processing';
import { patch } from '@web/core/utils/patch';

patch(PaymentPostProcessing, {

    /**
     * Los pagos con crédito interno quedan siempre "pendientes" (el pedido ya
     * está confirmado): no esperar a que pasen a "hecho" para ir a la página
     * de confirmación del pedido (igual que payment_custom).
     */
    getFinalStates(providerCode) {
        const finalStates = super.getFinalStates(...arguments);
        if (providerCode === 'credit') {
            finalStates.add('pending');
        }
        return finalStates;
    },

});
