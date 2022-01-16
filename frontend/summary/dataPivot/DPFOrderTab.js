import $ from "$";
import _ from "lodash";

import {_DataPivot_settings_spacers, buildHeaderTr, buildColGroup} from "./DataPivotUtilities";
import {NULL_CASE} from "./shared";
import DataPivotVisualization from "./DataPivotVisualization";
import buildFilterTable from "./FilterTable";
import buildFilterBooleanDiv from "./FilterLogic";
import buildSortingTable from "./SortTable";

let buildSpacingTable = function(tab, dp) {
        let tbody = $("<tbody>"),
            thead = $("<thead>").html(
                buildHeaderTr(["Row index", "Show line?", "Line style", "Extra space?", "Delete"])
            ),
            colgroup = buildColGroup(["", "", "", "", "120px"]),
            tbl = $('<table class="table table-sm table-bordered">').html([thead, colgroup, tbody]),
            settings = dp.settings.spacers,
            addDataRow = function(i) {
                let obj;
                if (!settings[i]) {
                    settings[i] = _DataPivot_settings_spacers.defaults();
                }
                obj = new _DataPivot_settings_spacers(dp, settings[i], i);
                tbody.append(obj.tr);
            },
            newDataRow = function() {
                addDataRow(settings.length);
            },
            newRowBtn = $(
                '<button class="btn btn-primary float-right"><i class="fa fa-fw fa-plus"></i>&nbsp;Add row</button>'
            ).on("click", newDataRow),
            numRows = settings.length === 0 ? 1 : settings.length;

        for (let i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append(
            newRowBtn,
            $("<h3>Additional row spacing</h3>"),
            '<p class="form-text text-muted">Add additional-space between rows, and optionally a horizontal line.</p>',
            tbl,
            "<hr/>"
        );
    },
    buildManualOverrideRows = function(dp, tbody) {
        let rows = [],
            get_selected_fields = function(v) {
                return v.field_name !== NULL_CASE;
            },
            descriptions = dp.settings.description_settings.filter(get_selected_fields),
            filters = dp.settings.filters.filter(get_selected_fields),
            sorts = dp.settings.sorts.filter(get_selected_fields),
            overrides = dp.settings.row_overrides,
            filter_logic = dp.settings.plot_settings.filter_logic,
            filter_query = dp.settings.plot_settings.filter_query,
            dataline = dp.settings.dataline_settings[0],
            datapoints = dp.settings.datapoint_settings,
            barchart = dp.settings.barchart,
            data;

        if (descriptions.length === 0) {
            rows.push(
                '<tr><td colspan="6">Please provide description columns before manually filtering.</td></tr>'
            );
            return tbody.html(rows);
        }

        // apply filters
        data = DataPivotVisualization.filter(dp.data, filters, filter_logic, filter_query);

        data = _.filter(
            data,
            _.partial(DataPivotVisualization.getIncludibleRows, _, dataline, datapoints, barchart)
        );

        if (data.length === 0) {
            rows.push('<tr><td colspan="6">No rows remaining after filtering criteria.</td></tr>');
            return tbody.html(rows);
        }

        // apply sorts
        data = DataPivotVisualization.sort_with_overrides(data, sorts, overrides);

        // apply manual index offsets
        let row_override_map = _.keyBy(overrides, "pk"),
            get_default = function(pk) {
                return {
                    pk,
                    include: true,
                    index: null,
                    text_style: NULL_CASE,
                    line_style: NULL_CASE,
                    symbol_style: NULL_CASE,
                };
            },
            get_matched_override_or_default = function(pk) {
                let match = row_override_map[pk];
                return match ? match : get_default(pk);
            };

        // build rows
        data.forEach(function(v) {
            let obj = get_matched_override_or_default(v._dp_pk),
                descs = descriptions.map(v2 => v[v2.field_name]).join("<br>"),
                include = $('<input name="ov_include" type="checkbox">').prop(
                    "checked",
                    obj.include
                ),
                index = $(
                    '<input name="ov_index" class="form-control" type="number" step="any">'
                ).val(obj.index),
                text_style = dp.style_manager.add_select("texts", obj.text_style, true),
                line_style = dp.style_manager.add_select("lines", obj.line_style, true),
                symbol_style = dp.style_manager.add_select("symbols", obj.symbol_style, true);

            let tr = $("<tr>")
                .data({pk: v._dp_pk, obj})
                .append($("<td>").html(descs))
                .append($("<td>").append(include))
                .append($("<td>").append(index))
                .append($('<td class="ov_text">').append(text_style))
                .append($('<td class="ov_line">').append(line_style))
                .append($('<td class="ov_symbol">').append(symbol_style));
            rows.push(tr);
        });

        return tbody.html(rows);
    },
    buildOrderingTable = function(tab, dp, tbody) {
        let thead = $("<thead>").html(
                buildHeaderTr([
                    "Description",
                    "Include",
                    "Row index",
                    "Override text style",
                    "Override line style",
                    "Override symbol style",
                ])
            ),
            resetOverrideRows = function() {
                if (!confirm("Remove all row-level customization settings?")) {
                    return;
                }
                dp.settings.row_overrides = [];
                buildManualOverrideRows(dp, tbody);
            },
            refreshRowsBtn = $(
                '<button class="btn btn-info float-right mr-2"><i class="fa fa-refresh"></i> Refresh</button>'
            ).on("click", () => buildManualOverrideRows(dp, tbody)),
            resetOverridesBtn = $(
                '<button class="btn btn-danger float-right"><i class="fa fa-trash"></i> Reset</button>'
            ).on("click", resetOverrideRows),
            tbl = $('<table class="table table-sm table-bordered table-hover tbl_override">').html([
                thead,
                tbody,
            ]);

        buildManualOverrideRows(dp, tbody);

        tab.append(
            resetOverridesBtn,
            refreshRowsBtn,
            $("<h3>Row-level customization</h3>"),
            '<p class="form-text text-muted">Row-level customization of individual rows after filtering/sorting above. Note that any changes to sorting or filtering will alter these customizations.</p>',
            tbl
        );
    },
    updateOverrideSettingState = function(dp, tbody) {
        dp.settings.row_overrides = [];
        tbody.find("tr").each(function(i, v) {
            let $v = $(v),
                obj = {
                    pk: $v.data("pk"),
                    include: $v.find('input[name="ov_include"]').prop("checked"),
                    index: parseFloat($v.find('input[name="ov_index"]').val()),
                    text_style: $v.find(".ov_text select option:selected").val(),
                    line_style: $v.find(".ov_line select option:selected").val(),
                    symbol_style: $v.find(".ov_symbol select option:selected").val(),
                };

            if (!_.isFinite(obj.index)) {
                delete obj.index;
            }

            // only add if settings are non-default
            if (
                obj.include === false ||
                obj.index !== undefined ||
                obj.text_style !== NULL_CASE ||
                obj.line_style !== NULL_CASE ||
                obj.symbol_style !== NULL_CASE
            ) {
                dp.settings.row_overrides.push(obj);
            }
        });
    },
    buildOrderingTab = function(dp) {
        let tab = $('<div class="tab-pane" id="data_pivot_settings_ordering">'),
            overrideTbody = $("<tbody>"),
            handleStateOverrideUpdate = function() {
                updateOverrideSettingState(dp, overrideTbody);
            };

        // add events to update override table
        overrideTbody
            .on("click", "button", handleStateOverrideUpdate)
            .on("change", "input,select", handleStateOverrideUpdate);

        // update whenever tab is clicked
        dp.$div.on("shown.bs.tab", 'a.dp_ordering_tab[data-toggle="tab"]', function() {
            buildManualOverrideRows(dp, overrideTbody);
        });

        // set a trigger if things have changed
        dp.store.setOverrideRefreshHandler(function() {
            let btn = $('<button class="btn btn-primary">Click to rebuild</button>').on(
                    "click",
                    () => buildManualOverrideRows(dp, overrideTbody)
                ),
                td = $('<td colspan="6">').append("<p>Row-ordering has changed.</p>", btn);
            overrideTbody.html($("<tr>").append(td));
        });

        buildFilterTable(tab, dp);
        buildFilterBooleanDiv(tab, dp);
        buildSortingTable(tab, dp);
        buildSpacingTable(tab, dp);
        buildOrderingTable(tab, dp, overrideTbody);
        return tab;
    };

export default buildOrderingTab;
