import $ from '$';
import _ from 'lodash';

import {
    _DataPivot_settings_filters,
    _DataPivot_settings_sorts,
    _DataPivot_settings_spacers,
    buildHeaderTr,
} from './DataPivotUtilities';
import { NULL_CASE } from './shared';
import DataPivotVisualization from './DataPivotVisualization';

let buildFilterTable = function(tab, dp, handleTableChange) {
        var thead = $('<thead>').html(
                buildHeaderTr(['Field name', 'Filter type', 'Value', 'Ordering'])
            ),
            tbody = $('<tbody>').on('change autocompletechange', 'input,select', handleTableChange),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.filters,
            addDataRow = function(i) {
                let obj;
                if (!settings[i]) {
                    settings[i] = _DataPivot_settings_filters.defaults();
                }
                obj = new _DataPivot_settings_filters(dp, settings[i]);
                tbody.append(obj.tr);
            },
            newDataRow = function() {
                addDataRow(settings.length);
                handleTableChange();
            },
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on(
                'click',
                newDataRow
            ),
            num_rows = settings.length === 0 ? 2 : settings.length;

        for (let i = 0; i < num_rows; i++) {
            addDataRow(i);
        }

        tab.append(
            $('<h3>Row filters</h3>').append(newRowBtn),
            '<p class="help-block">Use filters to determine which components of your dataset should be displayed on the figure.</p>',
            tbl
        );
    },
    buildFilterBooleanDiv = function(tab, dp, handleTableChange) {
        let div = $('<div>'),
            and = $('<label class="radio inline">AND</label>').append(
                '<input name="filter_logic" type="radio" value="and">'
            ),
            or = $('<label class="radio inline">OR</label>').append(
                '<input name="filter_logic" type="radio" value="or">'
            ),
            value = dp.settings.plot_settings.filter_logic || 'and';

        // set initial value
        if (value === 'and') {
            and.find('input').prop('checked', true);
        } else {
            or.find('input').prop('checked', true);
        }

        // set event binding to change settings
        div.on('change', 'input[name="filter_logic"]', function() {
            dp.settings.plot_settings.filter_logic = $('input[name="filter_logic"]:checked').val();
            handleTableChange();
        });

        div.append(
            '<h4>Filter logic</h4>',
            '<p class="help-block">Should multiple filter criteria be required for ALL rows (AND), or ANY row (OR)?</p>',
            and,
            or
        );

        tab.append(div, '<hr/>');
    },
    buildSortingTable = function(tab, dp, handleTableChange) {
        let thead = $('<thead>').html(buildHeaderTr(['Field name', 'Sort order', 'Ordering'])),
            tbody = $('<tbody>')
                .on('change', 'input,select', handleTableChange)
                .on('click', 'button', handleTableChange),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
            settings = dp.settings.sorts,
            addDataRow = function(i) {
                let obj;
                if (!settings[i]) {
                    settings[i] = _DataPivot_settings_sorts.defaults();
                }
                obj = new _DataPivot_settings_sorts(dp, settings[i], i);
                tbody.append(obj.tr);
            },
            newDataRow = function() {
                addDataRow(settings.length);
            },
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on(
                'click',
                newDataRow
            ),
            numRows = settings.length === 0 ? 2 : settings.length;

        for (let i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append(
            $('<h3>Row sorting</h3>').append(newRowBtn),
            '<p class="help-block">Sorting determines the order which rows will appear; sorts can be overridden using the manual override table below.</p>',
            tbl,
            '<hr/>'
        );
    },
    buildSpacingTable = function(tab, dp) {
        let tbody = $('<tbody>'),
            thead = $('<thead>').html(
                buildHeaderTr(['Row index', 'Show line?', 'Line style', 'Extra space?', 'Delete'])
            ),
            tbl = $('<table class="table table-condensed table-bordered">').html([thead, tbody]),
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
            newRowBtn = $('<button class="btn btn-primary pull-right">New row</button>').on(
                'click',
                newDataRow
            ),
            numRows = settings.length === 0 ? 1 : settings.length;

        for (let i = 0; i < numRows; i++) {
            addDataRow(i);
        }

        tab.append(
            $('<h3>Additional row spacing</h3>').append(newRowBtn),
            '<p class="help-block">Add additional-space between rows, and optionally a horizontal line.</p>',
            tbl,
            '<hr/>'
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
        data = DataPivotVisualization.filter(dp.data, filters, filter_logic);

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
        let row_override_map = _.keyBy(overrides, 'pk'),
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
                descs = descriptions.map((v2) => v[v2.field_name]).join('<br>'),
                include = $('<input name="ov_include" type="checkbox">').prop(
                    'checked',
                    obj.include
                ),
                index = $('<input name="ov_index" class="span12" type="number" step="any">').val(
                    obj.index
                ),
                text_style = dp.style_manager.add_select('texts', obj.text_style, true),
                line_style = dp.style_manager.add_select('lines', obj.line_style, true),
                symbol_style = dp.style_manager.add_select('symbols', obj.symbol_style, true);

            let tr = $('<tr>')
                .data({ pk: v._dp_pk, obj })
                .append($('<td>').html(descs))
                .append($('<td>').append(include))
                .append($('<td>').append(index))
                .append($('<td class="ov_text">').append(text_style))
                .append($('<td class="ov_line">').append(line_style))
                .append($('<td class="ov_symbol">').append(symbol_style));
            rows.push(tr);
        });

        return tbody.html(rows);
    },
    buildOrderingTable = function(tab, dp, tbody) {
        let thead = $('<thead>').html(
                buildHeaderTr([
                    'Description',
                    'Include',
                    'Row index',
                    'Override text style',
                    'Override line style',
                    'Override symbol style',
                ])
            ),
            resetOverrideRows = function() {
                if (!confirm('Remove all row-level customization settings?')) {
                    return;
                }
                dp.settings.row_overrides = [];
                buildManualOverrideRows(dp, tbody);
            },
            refreshRowsBtn = $(
                '<button class="btn btn-info" style="margin-left: 2em"><i class="fa fa-refresh"></i> Refresh</button>'
            ).on('click', () => buildManualOverrideRows(dp, tbody)),
            resetOverridesBtn = $(
                '<button class="btn btn-danger pull-right"><i class="fa fa-trash"></i> Reset</button>'
            ).on('click', resetOverrideRows),
            tbl = $(
                '<table class="table table-condensed table-bordered table-hover tbl_override">'
            ).html([thead, tbody]);

        buildManualOverrideRows(dp, tbody);

        tab.append(
            $('<h3>Row-level customization</h3>').append(refreshRowsBtn, resetOverridesBtn),
            '<p class="help-block">Row-level customization of individual rows after filtering/sorting above. Note that any changes to sorting or filtering will alter these customizations.</p>',
            tbl
        );
    },
    resetRowOrderOverrides = function(dp) {
        dp.settings.row_overrides.forEach(function(v) {
            v.index = null;
        });
    },
    showOverrideRebuildRequired = function(dp, tbody) {
        let btn = $('<button class="btn btn-primary">Click to rebuild</button>').on(
                'click',
                function() {
                    buildManualOverrideRows(dp, tbody);
                }
            ),
            td = $('<td colspan="6">').append('<p>Row-ordering has changed.</p>', btn);
        tbody.html($('<tr>').append(td));
    },
    updateOverrideSettingState = function(dp, tbody) {
        dp.settings.row_overrides = [];
        tbody.find('tr').each(function(i, v) {
            let $v = $(v),
                obj = {
                    pk: $v.data('pk'),
                    include: $v.find('input[name="ov_include"]').prop('checked'),
                    index: parseFloat($v.find('input[name="ov_index"]').val()),
                    text_style: $v.find('.ov_text select option:selected').val(),
                    line_style: $v.find('.ov_line select option:selected').val(),
                    symbol_style: $v.find('.ov_symbol select option:selected').val(),
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
            overrideTbody = $('<tbody>'),
            handleTableChange = function() {
                resetRowOrderOverrides(dp);
                showOverrideRebuildRequired(dp, overrideTbody);
            },
            handleStateOverrideUpdate = function() {
                updateOverrideSettingState(dp, overrideTbody);
            };

        // add events to update override table
        overrideTbody
            .on('click', 'button', handleStateOverrideUpdate)
            .on('change', 'input,select', handleStateOverrideUpdate);

        // update whenever tab is clicked
        dp.$div.on('shown', 'a.dp_ordering_tab[data-toggle="tab"]', function() {
            buildManualOverrideRows(dp, overrideTbody);
        });

        buildFilterTable(tab, dp, handleTableChange.bind(this));
        buildFilterBooleanDiv(tab, dp, handleTableChange.bind(this));
        buildSortingTable(tab, dp, handleTableChange.bind(this));
        buildSpacingTable(tab, dp);
        buildOrderingTable(tab, dp, overrideTbody);
        return tab;
    };

export default buildOrderingTab;
