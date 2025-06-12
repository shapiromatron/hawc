import $ from "$";

import {

    _DataPivot_settings_label,
    _DataPivot_settings_refline,
    _DataPivot_settings_refrect,
    buildColGroup,
    buildHeaderTr,
} from "./DataPivotUtilities";

let buildReferenceLines = function (tab, dp) {
        let thead = $("<thead>").html(
                buildHeaderTr(["Reference line value", "Line style", "Delete"])
            ),
            colgroup = buildColGroup(["", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.reference_lines,
            addDataRow = function (i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_refline.defaults());
                }
                obj = new _DataPivot_settings_refline(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function () {
                addDataRow(settings.length);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 1 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }
        tab.append(newRowBtn, $("<h3>Reference lines</h3>"), tbl);
    },
    buildReferenceRanges = function (tab, dp) {
        let thead = $("<thead>").html(
                buildHeaderTr(["Lower value", "Upper value", "Range style", "Delete"])
            ),
            colgroup = buildColGroup(["", "", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.reference_rectangles,
            addDataRow = function (i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_refrect.defaults());
                }
                obj = new _DataPivot_settings_refrect(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function () {
                addDataRow(settings.length);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 1 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append(newRowBtn, $("<h3>Reference ranges</h3>"), tbl);
    },
    buildReferenceLabels = function (tab, dp) {
        var thead = $("<thead>").html(buildHeaderTr(["Text", "Style", "Delete"])),
            colgroup = buildColGroup(["", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.labels,
            addDataRow = function (i) {
                let obj;
                if (!settings[i]) {
                    settings.push(_DataPivot_settings_label.defaults());
                }
                obj = new _DataPivot_settings_label(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function () {
                addDataRow(settings.length);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 1 : settings.length;

        for (let i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append(newRowBtn, $("<h3>Labels</h3>"), tbl);
    },
    buildReferenceTab = function (dp) {
        let tab = $('<div class="tab-pane" id="data_pivot_settings_ref">');
        buildReferenceLines(tab, dp);
        buildReferenceRanges(tab, dp);
        buildReferenceLabels(tab, dp);
        return tab;
    };

export default buildReferenceTab;
