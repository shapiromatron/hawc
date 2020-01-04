import $ from '$';

import { _DataPivot_settings_description, buildHeaderTr } from './DataPivotUtilities';

let buildDescriptionTable = function(tab, dp) {
        let thead = $('<thead>').html(
                buildHeaderTr([
                    'Column header',
                    'Display name',
                    'Header style',
                    'Text style',
                    'Maximum width (pixels)',
                    'On-click',
                    'Ordering',
                ])
            ),
            tbody = $('<tbody>'),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.description_settings,
            addDataRow = function(i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_description.defaults());
                }
                obj = new _DataPivot_settings_description(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function() {
                addDataRow(settings.length);
            },
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on(
                'click',
                newDataRow
            ),
            numRows = settings.length === 0 ? 5 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        return tab.append($('<h3>Descriptive text columns</h3>').append(newRowBtn), tbl);
    },
    buildDescriptionTab = function(dp) {
        let tab = $('<div class="tab-pane active" id="data_pivot_settings_description">');
        buildDescriptionTable(tab, dp);
        return tab;
    };

export default buildDescriptionTab;
