import $ from '$';

import {
    _DataPivot_settings_linedata,
    _DataPivot_settings_pointdata,
    _DataPivot_settings_barchart,
    buildHeaderTr,
} from './DataPivotUtilities';


const visSelectorId = 'visType',
    fpDiv = 'fpDiv',
    bcDiv = 'bcDiv';

let buildChartSelector = function(tab, dp){

        let asBarchart = (dp.settings.plot_settings.as_barchart)? 'selected': '',
            asForPlot = (!dp.settings.plot_settings.as_barchart)? 'selected': '';

        tab.prepend(`
           <h3>Visualization type</h3>
           <label class="checkbox control-label" for="${visSelectorId}">
                <select id="visType">
                    <option ${asForPlot}>Forest plot</option>
                    <option ${asBarchart}>Barchart</option>
                </select>
           </label>`);

        tab.on('change', '#'+visSelectorId, function(){
            if(this.value === 'Forest plot'){
                dp.settings.plot_settings.as_barchart = false;
                $('#'+fpDiv).show();
                $('#'+bcDiv).hide();
            } else {
                dp.settings.plot_settings.as_barchart = true;
                $('#'+fpDiv).hide();
                $('#'+bcDiv).show();
            }
        });

        dp.addOnRenderedCallback(function(){
            tab.find('#'+visSelectorId).trigger('change');
        });
    },
    buildDataPointTable = function(tab, dp){
        let thead = $('<thead>').html(buildHeaderTr([
                'Column header', 'Legend name', 'Marker style',
                'Conditional formatting', 'On-click', 'Ordering',
            ])),
            tbody = $('<tbody>'),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.datapoint_settings,
            addDataRow = function(i){
                let obj;
                if(!settings[i]){
                    settings.push(_DataPivot_settings_pointdata.defaults());
                }
                obj = new _DataPivot_settings_pointdata(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function(){
                let num_rows = settings.length;
                addDataRow(num_rows);
            },
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on('click', newDataRow),
            numRows = (settings.length === 0) ? 3 : settings.length;

        for(var i = 0; i < numRows; i++){
            addDataRow(i);
        }

        tab.append($('<h3>Data point options</h3>').append(newRowBtn));
        tab.append(tbl);
    },
    buildLineTable = function(tab, dp){
        let tbl, thead, tbody, obj,
            settings = dp.settings.dataline_settings;

        thead = $('<thead>').html(buildHeaderTr([
            'Column header', 'Legend name', 'Line style',
        ]));
        tbody = $('<tbody>');

        if(settings.length === 0){
            settings.push(_DataPivot_settings_linedata.defaults());
        }

        obj = new _DataPivot_settings_linedata(dp, 0);
        tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]);
        tbody.append(obj.tr);

        tab.append('<h3>Data point error-bar options</h3>', tbl);
    },
    buildBarChartDiv = function(tab, dp){
        tab.append(`
           <h3>Barchart settings</h3>
           <table class="table table-condensed table-bordered">
            <thead>
                <tr>
                    <th style="width: 20%">Column header</th>
                    <th style="width: 20%">Legend name</th>
                    <th style="width: 20%">Style</th>
                    <th style="width: 20%">Conditional formatting</th>
                    <th style="width: 20%">Other settings</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <label class="control-label" for="bc_field_name">Bar:</label>
                            <select id="bc_field_name" name="field_name" class="span12"></select></br>

                        <label class="control-label" for="bc_error_low_field_name">Error line low:</label>
                            <select id="bc_error_low_field_name" name="error_low_field_name" class="span12"></select></br>

                        <label class="control-label" for="bc_error_high_field_name">Error line high:</label>
                            <select id="bc_error_high_field_name" name="error_high_field_name" class="span12"></select></br>
                    </td>
                    <td>
                        <label class="control-label" for="bc_header_name">Bar:</label>
                            <input id="bc_header_name" name="header_name" type="text" class="span12"/></br>

                        <label class="control-label" for="bc_error_header_name">Error line:</label>
                            <input id="bc_error_header_name" name="error_header_name" type="text" class="span12"/></br>
                    </td>
                    <td>
                        <label class="control-label" for="bc_bar_style">Bar:</label>
                            <select id="bc_bar_style" name="bar_style" class="span12"><select/></br>

                        <label class="control-label" for="bc_error_marker_style">Error line:</label>
                            <select id="bc_error_marker_style" name="error_marker_style" class="span12"><select/></br>
                    </td>
                    <td>
                        <label class="control-label" for="bc_conditional_formatting">Bar:</label>
                        <input id="bc_conditional_formatting" name="conditional_formatting" type="text" /></br>
                    </td>
                    <td>
                        <label class="control-label" for="bc_dpe">On click:</label>
                            <select id="bc_dpe" name="dpe" class="span12"></select><br/>

                        <label class="control-label" for="bc_error_show_tails">Show error-line tails:</label>
                            <input id="bc_error_show_tails" name="error_show_tails" type="checkbox" /></br>
                    </td>
                </tr>
            </tbody>
           </table>
        `);
    },
    buildDataTab = function(dp){
        let tab = $('<div class="tab-pane" id="data_pivot_settings_data">'),
            forestPlotHolder = $(`<div id="${fpDiv}">`).appendTo(tab),
            barchartHolder = $(`<div id="${bcDiv}">`).appendTo(tab);

        buildChartSelector(tab, dp);
        buildDataPointTable(forestPlotHolder, dp);
        buildLineTable(forestPlotHolder, dp);
        buildBarChartDiv(barchartHolder, dp);
        tab.find('#'+visSelectorId).trigger('change');
        return tab;
    };

export default buildDataTab;
