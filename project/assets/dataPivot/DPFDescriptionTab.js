import $ from '$';

import {
    _DataPivot_settings_description,
} from './DataPivotUtilities';

let build_description_tab = function(self){
    var tab = $('<div class="tab-pane active" id="data_pivot_settings_description">'),
        headers = [
            'Column header', 'Display name', 'Header style',
            'Text style', 'Maximum width (pixels)', 'On-click', 'Ordering',
        ],
        tbody = $('<tbody>');

    var thead = $('<thead>').html(headers.map(function(v){return '<th>{0}</th>'.printf(v);}).join('\n')),
        add_row = function(i){
            if(!self.settings.description_settings[i]){
                self.settings.description_settings.push(_DataPivot_settings_description.defaults());
            }
            var obj = new _DataPivot_settings_description(self, self.settings.description_settings[i]);
            tbody.append(obj.tr);
        },
        new_row = function(){
            var num_rows = self.settings.description_settings.length;
            add_row(num_rows);
        },
        new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
            .on('click', new_row),
        num_rows = (self.settings.description_settings.length === 0) ? 5 :
            self.settings.description_settings.length;

    for(var i=0; i<num_rows; i++){
        add_row(i);
    }
    return tab.html([
        $('<h3>Descriptive text columns</h3>').append(new_point_button),
        $('<table class="table table-condensed table-bordered">').html([thead, tbody])]);
};

export default build_description_tab;
