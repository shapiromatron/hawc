import $ from "$";
import React from "react";
import ReactDOM from "react-dom";

import DescriptiveTable from "./components/DescriptiveTable";
import {_DataPivot_settings_description, buildHeaderTr, buildColGroup} from "./DataPivotUtilities";

let buildDescriptionTable = function(tab, dp) {
        let thead = $("<thead>").html(
                buildHeaderTr([
                    "Column header",
                    "Display name",
                    "Header style",
                    "Text style",
                    "Maximum width (pixels)",
                    "On-click",
                    "Ordering",
                ])
            ),
            colgroup = buildColGroup(["", "", "", "", "120px", "", "120px"]),
            tbody = $("<tbody>"),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
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
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 5 : settings.length;

        for (var i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        return tab.append([newRowBtn, $("<h3>Descriptive text columns</h3>")], tbl);
    },
    buildDescriptionTab = function(dp) {
        let tab = $('<div class="tab-pane active" id="data_pivot_settings_description">');
        buildDescriptionTable(tab, dp);
        const div = document.createElement("div");
        ReactDOM.render(<DescriptiveTable dp={dp} />, div);
        tab.append(div);
        return tab;
    };

export default buildDescriptionTab;
