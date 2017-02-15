import $ from '$';
import {
    _DataPivot_settings_refline,
    _DataPivot_settings_refrect,
    _DataPivot_settings_label,
} from './DataPivotUtilities';


let build_reference_tab = function(self){
    var tab = $('<div class="tab-pane" id="data_pivot_settings_ref">'),
        build_reference_lines = function(){
            var thead = $('<thead>').html(
                    [$('<tr>').append('<th>Reference line value</th><th>Line style</th><th>Delete</th>')]),
                tbody = $('<tbody>'),
                add_row = function(i){
                    if(!self.settings.reference_lines[i]){
                        self.settings.reference_lines.push(_DataPivot_settings_refline.defaults());
                    }
                    var obj = new _DataPivot_settings_refline(self, self.settings.reference_lines[i]);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.reference_lines.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
                    .on('click', new_row),
                num_rows = (self.settings.reference_lines.length === 0) ? 1 :
                    self.settings.reference_lines.length;

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }
            return $('<div>').append(
                      $('<h3>Reference lines</h3>').append(new_point_button),
                      $('<table class="table table-condensed table-bordered">').html([thead, tbody]));
        },
        build_reference_ranges = function(){
            var thead = $('<thead>').html(
                    [$('<tr>').append('<th>Lower value</th><th>Upper value</th><th>Range style</th><th>Delete</th>')]),
                colgroup = $('<colgroup><col style="width: 25%;"><col style="width: 25%;"><col style="width: 25%;"><col style="width: 25%;"></colgroup>'),
                tbody = $('<tbody>'),
                add_row = function(i){
                    if(!self.settings.reference_rectangles[i]){
                        self.settings.reference_rectangles.push(_DataPivot_settings_refrect.defaults());
                    }
                    var obj = new _DataPivot_settings_refrect(self, self.settings.reference_rectangles[i]);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.reference_rectangles.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
                    .on('click', new_row),
                num_rows = (self.settings.reference_rectangles.length === 0) ? 1 :
                    self.settings.reference_rectangles.length;

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }
            return $('<div>').append(
                $('<h3>Reference ranges</h3>').append(new_point_button),
                $('<table class="table table-condensed table-bordered">').html([colgroup, thead, tbody]));
        },
        build_labels = function(){
            var thead = $('<thead>').html(
                    [$('<tr>').append('<th>Text</th><th>Style</th><th>Delete</th>')]),
                tbody = $('<tbody>'),
                add_row = function(i){
                    if(!self.settings.labels[i]){
                        self.settings.labels.push(_DataPivot_settings_label.defaults());
                    }
                    var obj = new _DataPivot_settings_label(self, self.settings.labels[i]);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.labels.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
                    .on('click', new_row),
                num_rows = (self.settings.labels.length === 0) ? 1 :
                    self.settings.labels.length;

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }
            return $('<div>').append(
                    $('<h3>Labels</h3>').append(new_point_button),
                    $('<table class="table table-condensed table-bordered">').html([thead, tbody]));
        };

    return tab.html([
        build_reference_lines(),
        build_reference_ranges(),
        build_labels(),
    ]);
};

export default build_reference_tab;
