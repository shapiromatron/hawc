import _ from 'underscore';
import $ from '$';

import RoBHeatmap from 'summary/RoBHeatmap';

import BaseVisualForm from './BaseVisualForm';
import RoBMetricTable from './RoBMetricTable';
import {
    TextField,
    IntegerField,
    CheckboxField,
    SelectField,
} from './Fields';


class RoBHeatmapForm extends BaseVisualForm {

    buildPreview($parent, data){
        this.preview = new RoBHeatmap(data).displayAsPage( $parent.empty(), {'dev': true} );
    }

    initDataForm(){
        _.each(['system', 'organ', 'effect', 'effect_subtype'], function(d){
            $('#id_prefilter_{0}'.printf(d)).on('change', function(){
                var div = $('#div_id_{0}s'.printf(d));
                ($(this).prop('checked')) ? div.show(1000) : div.hide(0);
            }).trigger('change');
        });
    }

    updateSettingsFromPreview(){
        var plotSettings = JSON.stringify(this.preview.data.settings);
        $('#id_settings').val(plotSettings);
        this.unpackSettings();
    }

}

_.extend(RoBHeatmapForm, {
    tabs: [
        {name: 'overall', label: 'General settings'},
        {name: 'metrics', label: 'Included metrics'},
        {name: 'legend',  label: 'Legend settings'},
    ],
    schema: [
        {
            type: TextField,
            name: 'title',
            label: 'Title',
            def: '',
            tab: 'overall',
        },
        {
            type: TextField,
            name: 'xAxisLabel',
            label: 'X-axis label',
            def: '',
            tab: 'overall',
        },
        {
            type: TextField,
            name: 'yAxisLabel',
            label: 'Y-axis label',
            def: '',
            tab: 'overall',
        },
        {
            type: IntegerField,
            name: 'padding_top',
            label: 'Plot padding-top (px)',
            def: 20,
            tab: 'overall',
        },
        {
            type: IntegerField,
            name: 'cell_size',
            label: 'Cell-size (px)',
            def: 40,
            tab: 'overall',
        },
        {
            type: IntegerField,
            name: 'padding_right',
            label: 'Plot padding-right (px)',
            def: 10,
            tab: 'overall',
        },
        {
            type: IntegerField,
            name: 'padding_bottom',
            label: 'Plot padding-bottom (px)',
            def: 35,
            tab: 'overall',
        },
        {
            type: IntegerField,
            name: 'padding_left',
            label: 'Plot padding-left (px)',
            def: 20,
            tab: 'overall',
        },
        {
            type: SelectField,
            name: 'x_field',
            label: 'X-axis field',
            opts: [
                ['study', 'Study'],
                ['metric', 'RoB metric'],
            ],
            def: 'study',
            tab: 'overall',
        },
        {
            type: RoBMetricTable,
            prependSpacer: false,
            label: 'Included metrics',
            name: 'included_metrics',
            colWidths: [10, 90],
            addBlankRowIfNone: false,
            tab: 'metrics',
        },
        {
            type: CheckboxField,
            name: 'show_legend',
            label: 'Show legend',
            def: true,
            tab: 'legend',
        },
        {
            type: CheckboxField,
            name: 'show_na_legend',
            label: 'Show N/A in legend',
            def: true,
            helpText: 'Show "Not applicable" in the legend',
            tab: 'legend',
        },
        {
            type: CheckboxField,
            name: 'show_nr_legend',
            label: 'Show NR in legend',
            def: true,
            helpText: 'Show "Not reported" in the legend',
            tab: 'legend',
        },
        {
            type: IntegerField,
            name: 'legend_x',
            label: 'Legend x-location (px)',
            def: -1,
            helpText: 'Set to -1 to be at the left, or 9999 to be at the right',
            tab: 'legend',
        },
        {
            type: IntegerField,
            name: 'legend_y',
            label: 'Legend y-location (px)',
            def: 9999,
            helpText: 'Set to -1 to be at the top, or 9999 to be at the bottom',
            tab: 'legend',
        },
    ],
});

export default RoBHeatmapForm;
