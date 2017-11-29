import $ from '$';
import _ from 'lodash';


class DoseUnitsWidget {

    constructor (form, opts){
        form.on('submit', this.handleFormSubmit.bind(this));
        this.init(opts);
    }

    init(opts){
        this.$input = $(opts.el).hide();
        this.$widgetDiv = $('#pduDiv');
        this.$available = $('#pduAvailable');
        this.$selected = $('#pduSelected');
        $('#pduAdd').on('click', this.handleAdd.bind(this));
        $('#pduRemove').on('click', this.handleRemove.bind(this));
        $('#pduUp').on('click', this.handleUp.bind(this));
        $('#pduDown').on('click', this.handleDown.bind(this));
        $.get(opts.api, this.render.bind(this));
    }

    handleAdd(){
        // add new units, after de-duping those already available.
        var optsMap = {};
        this.$available.find('option:selected').each(function(i, el){
            optsMap[el.value] = el;
        });
        this.$selected.find('option').each(function(i, el){
            delete optsMap[el.value];
        });
        this.$selected.append($(_.values(optsMap)).clone());
    }

    handleRemove(){
        this.$selected.find('option:selected').remove();
    }

    handleUp(){
        this.$selected.find('option:selected')
            .each(function(i, el){
                var $el = $(el);
                $el.insertBefore($el.prev());
            });
    }

    handleDown(){
        this.$selected.find('option:selected')
            .get().reverse().forEach(function(el){
                var $el = $(el);
                $el.insertAfter($el.next());
            });
    }

    handleFormSubmit(){
        var selected_ids = this.$selected.children()
                .map(function(i, el){return parseInt(el.value);})
                .get();
        this.$input.val(selected_ids.join(','));
        return true;
    }

    render(objects){
        var self = this;

        // set available
        objects.forEach(function(d){
            self.$available.append('<option value="{0}">{1}</option>'.printf(d.id, d.name));
        });

        //set selected
        var objectsKeymap = _.keyBy(objects, 'id'),
            ids = this.$input.val().split(',')
                .filter(function(d){return d.length>0;})
                .map(function(d){return parseInt(d);});

        ids.forEach(function(d){
            var dose = objectsKeymap[d];
            self.$selected.append('<option value="{0}">{1}</option>'.printf(dose.id, dose.name));
        });

        //render on DOM
        this.$input.parent().prepend(this.$widgetDiv);
        this.$widgetDiv.show();
    }
}

export default DoseUnitsWidget;
