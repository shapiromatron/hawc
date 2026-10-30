import $ from "$";

import {
    _DataPivot_settings_calculated,
    _DataPivot_settings_description,
    buildColGroup,
    buildHeaderTr,
} from "./DataPivotUtilities";

let buildDescriptionTable = function (tab, dp) {
        let thead = $("<thead>").html(
                buildHeaderTr([
                    "Column header",
                    "Display name",
                    "Header style",
                    "Text style",
                    "Maximum width (pixels)",
                    "To right",
                    "On-click",
                    "Ordering",
                ])
            ),
            colgroup = buildColGroup(["", "", "", "", "", "", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.description_settings,
            addDataRow = function (i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_description.defaults());
                }
                obj = new _DataPivot_settings_description(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function () {
                addDataRow(settings.length);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 5 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        return tab.append([newRowBtn, $("<h3>Descriptive text columns</h3>")], tbl);
    },
    buildCalculatedTable = function (tab, dp) {
        let thead = $("<thead>").html(buildHeaderTr(["Column name", "Column formula", "Delete"])),
            colgroup = buildColGroup(["200px", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.calculated_columns,
            addDataRow = i => {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_calculated.defaults());
                }
                obj = new _DataPivot_settings_calculated(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", () => addDataRow(settings.length)),
            numRows = settings.length === 0 ? 2 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        return tab.append(
            [newRowBtn, $("<h3>Calculated columns</h3>")],
            tbl,
            `<div class="text-muted-text">
                <p>Build new columns from existing columns. The mini-language is described below:</p>
                <ul>
                    <li><code>\${COLNAME}</code>: print a column value</li>
                    <li><code>\${round(COLNAME,2)}</code>: rounds a column to 2 decimal points</li>
                    <li><code>exists(COLNAME)?hello:world</code>: if COLNAME is not empty, print hello, else world</li>
                    <li><code>match(COLNAME,"hello")?hello:goodbye</code>: if COLNAME equals "hello", print hello, else goodbye</li>

                </ul>
                <p>You can compose the language to build complex strings, for example: <code>\${response} ± round(stdev,2) (round(percent control mean,1)%)</code>. We are in the process of writing better documentation with examples. Please contact us if you'd like sooner!</p>
            </div>`
        );
    },
    buildDescriptionTab = function (dp) {
        let tab = $('<div class="tab-pane active" id="data_pivot_settings_description">');
        buildDescriptionTable(tab, dp);
        buildCalculatedTable(tab, dp);
        return tab;
    };

export default buildDescriptionTab;
