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

let buildChartSelector = function(tab, dp) {
        let asBarchart = dp.settings.plot_settings.as_barchart ? 'selected' : '',
            asForPlot = !dp.settings.plot_settings.as_barchart ? 'selected' : '';

        tab.prepend(`
           <h3>Visualization type</h3>
           <label class="checkbox control-label" for="${visSelectorId}">
                <select id="visType">
                    <option ${asForPlot}>Forest plot</option>
                    <option ${asBarchart}>Barchart</option>
                </select>
           </label>`);

        tab.on('change', '#' + visSelectorId, function() {
            if (this.value === 'Forest plot') {
                dp.settings.plot_settings.as_barchart = false;
                $('#' + fpDiv).show();
                $('#' + bcDiv).hide();
            } else {
                dp.settings.plot_settings.as_barchart = true;
                $('#' + fpDiv).hide();
                $('#' + bcDiv).show();
            }
        });

        dp.addOnRenderedCallback(function() {
            tab.find('#' + visSelectorId).trigger('change');
        });
    },
    buildDataPointTable = function(tab, dp) {
        let thead = $('<thead>').html(
                buildHeaderTr([
                    'Column header',
                    'Legend name',
                    'Marker style',
                    'Conditional formatting',
                    'On-click',
                    'Ordering',
                ])
            ),
            tbody = $('<tbody>'),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.datapoint_settings,
            addDataRow = function(i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_pointdata.defaults());
                }
                obj = new _DataPivot_settings_pointdata(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function() {
                let num_rows = settings.length;
                addDataRow(num_rows);
            },
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on(
                'click',
                newDataRow
            ),
            numRows = settings.length === 0 ? 3 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append($('<h3>Data point options</h3>').append(newRowBtn));
        tab.append(tbl);
    },
    buildLineTable = function(tab, dp) {
        let tbl,
            thead,
            tbody,
            obj,
            settings = dp.settings.dataline_settings;

        thead = $('<thead>').html(buildHeaderTr(['Column header', 'Legend name', 'Line style']));
        tbody = $('<tbody>');

        if (settings.length === 0) {
            settings.push(_DataPivot_settings_linedata.defaults());
        }

        obj = new _DataPivot_settings_linedata(dp, 0);
        tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]);
        tbody.append(obj.tr);

        tab.append('<h3>Data point error-bar options</h3>', tbl);
    },
    buildBarChartDiv = function(tab, dp) {
        let obj = new _DataPivot_settings_barchart(dp);
        tab.append(obj.div);
    },
    buildDataTab = function(dp) {
        let tab = $('<div class="tab-pane" id="data_pivot_settings_data">'),
            forestPlotHolder = $(`<div id="${fpDiv}">`).appendTo(tab),
            barchartHolder = $(`<div id="${bcDiv}">`).appendTo(tab);

        buildChartSelector(tab, dp);
        buildDataPointTable(forestPlotHolder, dp);
        buildLineTable(forestPlotHolder, dp);
        buildBarChartDiv(barchartHolder, dp);
        tab.find('#' + visSelectorId).trigger('change');
        return tab;
    };

export default buildDataTab;
