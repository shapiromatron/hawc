import {Provider, inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import $ from "$";

import BaseVisual from "./BaseVisual";
import ExploreHeatmapPlot from "./ExploreHeatmapPlot";
import {addLabelAction, addLabelIndicators, handleVisualError} from "./common";
import {NULL_VALUE} from "./constants";
import DatasetTable from "./heatmap/DatasetTable";
import FilterWidgetContainer from "./heatmap/FilterWidgetContainer";
import HeatmapDatastore from "./heatmap/HeatmapDatastore";

const startupHeatmapAppRender = function (el, settings, datastore, options) {
    const store = new HeatmapDatastore(settings, datastore, options);
    try {
        if (store.withinRenderableBounds) {
            store.initialize();
        }
        ReactDOM.render(
            <Provider store={store}>
                <ExploreHeatmapComponent options={options} />
            </Provider>,
            el
        );
    } catch (err) {
        handleVisualError(err, $(el));
    }
};

@inject("store")
@observer
class ExploreHeatmapComponent extends Component {
    componentDidMount() {
        const {store} = this.props,
            id = store.settingsHash,
            el = document.getElementById(id),
            tooltipEl = document.getElementById(`tooltip-${id}`);

        if (el) {
            new ExploreHeatmapPlot(store, this.props.options).render(el, tooltipEl);
        }
    }
    render() {
        const {store} = this.props,
            id = store.settingsHash,
            hasFilters = store.settings.filter_widgets.length > 0;

        if (!store.hasDataset) {
            return <Alert message={"No data are available."} />;
        }

        if (!store.withinRenderableBounds) {
            const {n_rows, n_cols, n_cells, maxCells} = this.props.store,
                message = `This heatmap is too large and cannot be rendered. Using the settings specified, the current heatmap will have ${n_rows} rows, ${n_cols} columns, and ${n_cells} cells. Please change the settings to have fewer than ${maxCells} cells.`;
            return <Alert message={message} />;
        }

        return (
            <>
                <div style={{display: "flex", flexDirection: "row"}}>
                    <div style={{flex: 9}}>
                        <div id={id}>
                            <Loading />
                        </div>
                    </div>
                    {hasFilters ? (
                        <div
                            className="col-3 ml-2"
                            style={{
                                display: "flex",
                                flex: 3,
                                minWidth: 300,
                                maxWidth: 400,
                            }}>
                            <FilterWidgetContainer />
                        </div>
                    ) : null}
                    <div id={`tooltip-${id}`} style={{position: "absolute"}}></div>
                </div>
                <DatasetTable />
            </>
        );
    }
}
ExploreHeatmapComponent.propTypes = {
    store: PropTypes.object,
    options: PropTypes.object.isRequired,
};

class ExploreHeatmap extends BaseVisual {
    constructor(data, dataset) {
        super(data);
        this.dataset = dataset || null;
    }

    getSettings() {
        const {settings} = this.data;
        return {
            cell_height: settings.cell_height,
            cell_width: settings.cell_width,
            color_range: settings.color_range,
            compress_x: settings.compress_x,
            compress_y: settings.compress_y,
            filter_widgets: settings.filter_widgets,
            padding: settings.padding,
            show_axis_border: settings.show_axis_border,
            show_grid: settings.show_grid,
            show_counts: settings.show_counts,
            show_tooltip: settings.show_tooltip,
            show_totals: settings.show_totals,
            show_null: settings.show_null,
            filters: settings.filters,
            filtersLogic: settings.filtersLogic,
            filtersQuery: settings.filtersQuery,
            autosize_cells: settings.autosize_cells,
            autorotate_tick_labels: settings.autorotate_tick_labels,
            table_fields: settings.table_fields.filter(d => d.column !== NULL_VALUE),
            hawc_interactivity: settings.hawc_interactivity,
            title: settings.title,
            x_fields: settings.x_fields.filter(d => d.column !== NULL_VALUE),
            x_label: settings.x_label,
            x_tick_rotate: settings.x_tick_rotate,
            y_fields: settings.y_fields.filter(d => d.column !== NULL_VALUE),
            y_label: settings.y_label,
            y_tick_rotate: settings.y_tick_rotate,
            x_axis_bottom: settings.x_axis_bottom,
            count_column: settings.count_column,
        };
    }

    getDataset(callback) {
        const url = this.data.settings.data_url;
        if (this.dataset) {
            callback({dataset: this.dataset});
        } else {
            fetch(url, h.fetchGet)
                .then(response => response.json())
                .then(json => {
                    this.dataset = json;
                    return {dataset: json};
                })
                .then(callback, error => {
                    callback({error});
                });
        }
    }

    addActionsMenu(isEditable) {
        let {data_url} = this.data.settings,
            csv_url = data_url.includes("?") ? `${data_url}&format=csv` : `${data_url}?format=csv`,
            csv_text = `<i class="fa fa-file-text-o"></i> Download dataset (csv)`,
            xlsx_url = data_url.includes("?")
                ? `${data_url}&format=xlsx`
                : `${data_url}?format=xlsx`,
            xlsx_text = `<i class="fa fa-file-excel-o"></i> Download dataset (xlsx)`,
            opts = [];

        if (isEditable) {
            opts.push(
                ...[
                    "Visualization editing",
                    {href: this.data.url_update, text: '<i class="fa fa-edit"></i>&nbsp;Update'},
                    {href: this.data.url_delete, text: '<i class="fa fa-trash"></i>&nbsp;Delete'},
                    addLabelAction(this.data.label_htmx),
                ]
            );
        }
        opts.push(
            ...["Dataset", {href: csv_url, text: csv_text}, {href: xlsx_url, text: xlsx_text}]
        );
        return HAWCUtils.pageActionsButton(opts);
    }

    displayAsPage($el, options) {
        options = options || {};

        var title = $("<h2>").text(this.data.title),
            labelIndicators = addLabelIndicators(this.data.label_indicators_htmx),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            callback = resp => {
                if (resp.dataset || resp.error) {
                    // exit early if we got an error
                    if (resp.error) {
                        HAWCUtils.addAlert(resp.error, $plotDiv);
                        $el.empty().append($plotDiv);
                        return;
                    }

                    try {
                        const settings = this.getSettings(),
                            dataset = resp.dataset,
                            actions = this.data.title
                                ? this.addActionsMenu(window.isEditable)
                                : null;

                        $el.empty().append($plotDiv);

                        if (!options.visualOnly) {
                            var headerRow = $('<div class="d-flex">').append([
                                title,
                                labelIndicators,
                                HAWCUtils.unpublished(this.data.published, window.isEditable),
                                actions,
                            ]);
                            $el.prepend(headerRow).append(captionDiv);
                        }

                        startupHeatmapAppRender($plotDiv[0], settings, dataset, options);
                    } catch (err) {
                        return handleVisualError(err, $plotDiv);
                    }

                    if (options.cb) {
                        options.cb(this);
                    }

                    caption.renderAndEnable();
                } else {
                    throw "Unknown status.";
                }
            };

        this.getDataset(callback);
    }

    displayAsModal(options) {
        // TODO HEATMAP  - check!
        options = options || {};

        var captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal(),
            callback = resp => {
                // exit early if we got an error
                if (resp.error) {
                    const $errDiv = $("<div>");
                    HAWCUtils.addAlert(resp.error, $errDiv);
                    modal
                        .addHeader([
                            $("<h4>").text(this.data.title),
                            HAWCUtils.unpublished(this.data.published, window.isEditable),
                        ])
                        .addBody($errDiv)
                        .addFooter("")
                        .show({maxWidth: 1200});
                    return;
                }

                const settings = this.getSettings(),
                    dataset = resp.dataset;

                modal.getModal().on("shown.bs.modal", function () {
                    try {
                        startupHeatmapAppRender($plotDiv[0], settings, dataset, options);
                    } catch (err) {
                        return handleVisualError(err, $plotDiv);
                    }
                    caption.renderAndEnable();
                });

                modal
                    .addHeader([
                        $("<h4>").text(this.data.title),
                        HAWCUtils.unpublished(this.data.published, window.isEditable),
                    ])
                    .addBody([$plotDiv, captionDiv])
                    .addFooter("")
                    .show({maxWidth: 1200});
            };

        options = options || {};
        this.getDataset(callback);
    }
}

export default ExploreHeatmap;
