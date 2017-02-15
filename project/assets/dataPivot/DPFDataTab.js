import $ from '$';

import {
    _DataPivot_settings_linedata,
    _DataPivot_settings_pointdata,
} from './DataPivotUtilities';


let build_data_tab = function(self){
    var tab = $('<div class="tab-pane" id="data_pivot_settings_data">'),
        headers = ['Column header', 'Display name', 'Line style'],
        header_tr = function(lst){
            var vals = [];
            lst.forEach(function(v){vals.push('<th>{0}</th>'.printf(v));});
            return $('<tr>').html(vals);
        };

    //Build line table
    var thead = $('<thead>').html(header_tr(headers)),
        tbody = $('<tbody>');

    if(self.settings.dataline_settings.length === 0){
        self.settings.dataline_settings.push(_DataPivot_settings_linedata.defaults());
    }

    var obj = new _DataPivot_settings_linedata(self, 0),
        tbl_line = $('<table class="table table-condensed table-bordered">').html([thead, tbody]);

    tbody.append(obj.tr);

    // Build point table
    headers = ['Column header', 'Display name', 'Marker style', 'Conditional formatting', 'On-click'];
    headers.push('Ordering');
    thead = $('<thead>').html(header_tr(headers));
    var point_tbody = $('<tbody>');

    var add_point_data_row = function(i){
            if(!self.settings.datapoint_settings[i]){
                self.settings.datapoint_settings.push(_DataPivot_settings_pointdata.defaults());
            }
            obj = new _DataPivot_settings_pointdata(self, self.settings.datapoint_settings[i]);
            point_tbody.append(obj.tr);
        }, new_point_row = function(){
            var num_rows = self.settings.datapoint_settings.length;
            add_point_data_row(num_rows);
        }, num_rows = (self.settings.datapoint_settings.length === 0) ? 3 : self.settings.datapoint_settings.length,
        new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_point_row),
        tbl_points = $('<table class="table table-condensed table-bordered">').html([thead, point_tbody]);

    for(var i=0; i<num_rows; i++){
        add_point_data_row(i);
    }

    return tab.html([
        $('<h3>Data point options</h3>').append(new_point_button),
        tbl_points,
        '<h3>Data point error-bar options</h3>',
        tbl_line,
    ]);
};

export default build_data_tab;
