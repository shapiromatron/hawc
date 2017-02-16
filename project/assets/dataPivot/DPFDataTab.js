import $ from '$';

import {
    _DataPivot_settings_linedata,
    _DataPivot_settings_pointdata,
} from './DataPivotUtilities';


let headerTr = function(lst){
        return $('<tr>').html(lst.map((v)=>`<th>${v}</th>`).join());
    },
    buildDataPointTable = function(tab, dp){
        let thead = $('<thead>'),
            tbody = $('<tbody>'),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.datapoint_settings;

        // Build point table
        thead.html(headerTr([
            'Column header', 'Display name', 'Marker style',
            'Conditional formatting', 'On-click', 'Ordering',
        ]));

        let addDataRow = function(i){
                let obj;
                if(!settings[i]){
                    settings.push(_DataPivot_settings_pointdata.defaults());
                }
                obj = new _DataPivot_settings_pointdata(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newRow = function(){
                let num_rows = settings.length;
                addDataRow(num_rows);
            },
            num_rows = (settings.length === 0) ? 3 : settings.length,
            new_point_button = $('<button class="btn btn-primary pull-right">New row</button>').on('click', newRow);

        for(var i=0; i<num_rows; i++){
            addDataRow(i);
        }

        tab.append($('<h3>Data point options</h3>').append(new_point_button));
        tab.append(tbl);
    },
    buildLineTable = function(tab, dp){
        let tbl, thead, tbody, obj;

        thead = $('<thead>').html(headerTr([
            'Column header', 'Display name', 'Line style',
        ]));
        tbody = $('<tbody>');

        if(dp.settings.dataline_settings.length === 0){
            dp.settings.dataline_settings.push(
                _DataPivot_settings_linedata.defaults());
        }

        obj = new _DataPivot_settings_linedata(dp, 0);
        tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]);
        tbody.append(obj.tr);

        tab.append('<h3>Data point error-bar options</h3>', tbl);
    },
    buildDataTab = function(self){
        let tab = $('<div class="tab-pane" id="data_pivot_settings_data">');
        buildDataPointTable(tab, self);
        buildLineTable(tab, self);
        return tab;
    };

export default buildDataTab;
