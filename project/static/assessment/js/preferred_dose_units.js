var DoseUnitsWidget = function(opts){
    this.$el = $(opts.el);
    this.$selected = null;
    this.api = opts.api;
    this.init();
};
DoseUnitsWidget.prototype = {
    init: function(){
        var self = this;
        this.$el.hide();
        $.get(this.api, function(objects){
            self.renderSelectors(objects);
        });
    },
    renderSelectors(objects){
        var $available = $('<select multiple="true" size="10" >'),
            $selected = $('<select multiple="true" size="10" >');

        // set available
        objects.forEach(function(d){
            $available.append('<option value="{0}">{1}</option>'.printf(d.id, d.name));
        });

        //set selected
        var objectsKeymap = _.indexBy(objects, 'id'),
            ids = this.$el.val().split(',')
            .filter(function(d){return d.length>0;})
            .map(function(d){return parseInt(d);});

        ids.forEach(function(d){
            var dose = objectsKeymap[d];
            $selected.append('<option value="{0}">{1}</option>'.printf(dose.id, dose.name));
        });

        //render on DOM
        this.$el.parent().prepend($available, $selected);
        this.$selected = $selected;
    },
    handleFormSubmit(){
        var selected_ids = this.$selected.children()
                .map(function(i, el){return parseInt(el.value);})
                .get();
        this.$el.val(selected_ids.join(','));
    }
};

// TODO - use a Django-template to render the template for this thingy. init should
// bind to all the components here, don't waste time in jQuery building this stuff.
