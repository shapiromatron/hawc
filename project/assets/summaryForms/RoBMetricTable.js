import _ from 'underscore';
import $ from '$';

import {
    TableField,
} from './TableFields';


class RoBMetricTable extends TableField{

    renderHeader(){
        return $('<tr>')
            .append(
                '<th>Include in visual</th>',
                '<th>Metric</th>'
            ).appendTo(this.$thead);
    }

    addRow(){
        var includeTd = this.addTdCheckbox('included', true),
            metricTd = this.addTdP('metric', '');

        return $('<tr>')
            .append(
                includeTd,
                metricTd
            ).appendTo(this.$tbody);
    }

    fromSerialized(){
        // override this method to include all metrics,
        // even those not included in serialization.
        var metrics = window.rob_metrics,
            selected = this.parent.settings[this.schema.name] || [],
            func;

        // by default select all metrics if none are selected
        func = (selected.length === 0)?
                function(d){d.included = true;}:
                function(d){d.included = _.contains(selected, d.id);};

        _.each(metrics, func);
        this.$tbody.empty();
        _.each(metrics, this.fromSerializedRow, this);
    }

    fromSerializedRow(d){
        var row = this.addRow();
        row.find('.metric').text(d.metric);
        row.find('input[name="included"]')
            .prop('checked', d.included)
            .data('id', d.id);
    }

    toSerializedRow(row){
        var inp = $(row).find('input[name="included"]');
        return inp.prop('checked')?
            inp.data('id'):
            null;
    }

}

export default RoBMetricTable;
