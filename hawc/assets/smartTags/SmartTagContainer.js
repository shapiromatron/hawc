import $ from '$';

import SmartTagModal from './SmartTagModal';
import SmartTagInline from './SmartTagInline';

class SmartTagContainer {
    constructor($el, options) {
        this.options = options || {};
        this.$el = $el;
        if (this.options.showOnStartup) {
            this.renderAndEnable();
        }
    }

    static toggleAllModals(el) {
        $(el)
            .find('span.smart-tag')
            .each(function() {
                let st = $(this).data('_smartTag');
                if (!st) {
                    st = new SmartTagModal(this);
                }
                if (st.isActive) {
                    st.disable();
                } else {
                    st.enable();
                }
            });
    }

    renderAndEnable() {
        this.renderInlines();
        this.enableModals();
    }

    unrenderAndDisable() {
        this.unrenderInlines();
        this.disableModals();
    }

    renderInlines() {
        this.$el.find('div.smart-tag').each(function() {
            let st = $(this).data('_smartTag');
            if (!st) {
                st = new SmartTagInline(this);
            }
            st.render();
        });
    }

    unrenderInlines($el) {
        this.$el.find('div.smart-tag').each(function() {
            let st = $(this).data('_smartTag');
            if (!st) {
                st = new SmartTagInline(this);
            }
            st.unrender();
        });
    }

    enableModals() {
        this.$el.find('span.smart-tag').each(function() {
            let st = $(this).data('_smartTag');
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.enable();
        });
    }

    disableModals() {
        this.$el.find('span.smart-tag').each(function() {
            let st = $(this).data('_smartTag');
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.disable();
        });
    }
}

export default SmartTagContainer;
