import SmartTag from './SmartTag';


class SmartTagContainer {

    constructor($el, options){
        options = options || {};
        this.$el = $el;

        this.$el.on('SmartTagContainerReady', function(){
            SmartTag.initialize_tags($el);
        });

        if (options.showOnStartup){
            this.ready();
        }
    }

    ready(){
        this.$el.trigger('SmartTagContainerReady');
    }

    getEl(){
        return this.$el;
    }

}

export default SmartTagContainer;
