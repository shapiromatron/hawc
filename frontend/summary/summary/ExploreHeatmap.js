import $ from "$";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer, Provider} from "mobx-react";

import h from "shared/utils/helpers";
import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import Loading from "shared/components/Loading";
import BaseVisual from "./BaseVisual";
import HAWCModal from "utils/HAWCModal";
import DatasetTable from "./heatmap/DatasetTable";
import FilterWidgetContainer from "./heatmap/FilterWidgetContainer";
import ExploreHeatmapPlot from "./ExploreHeatmapPlot";
import {NULL_VALUE} from "./constants";
import HeatmapDatastore from "./heatmap/HeatmapDatastore";

let startupHeatmapAppRender = function(el, settings, datastore, options) {
    const store = new HeatmapDatastore(settings, datastore, options);
    ReactDOM.render(
        <Provider store={store}>
            <ExploreHeatmapComponent options={options} />
        </Provider>,
        el
    );
};

@inject("store")
@observer
class ExploreHeatmapComponent extends Component {
    componentDidMount() {
        const {store} = this.props,
            {settings} = store,
            id = h.hashString(JSON.stringify(settings)),
            el = document.getElementById(id),
            tooltipEl = document.getElementById(`tooltip-${id}`);
        new ExploreHeatmapPlot(store, this.props.options).render(el, tooltipEl);
    }
    render() {
        const {store} = this.props,
            {dataset, settings} = store,
            id = h.hashString(JSON.stringify(settings)),
            hasFilters = settings.filter_widgets.length > 0;

        if (dataset === null || dataset.length === 0) {
            return <div className="alert alert-danger">No data are available.</div>;
        }

        return (
            <div style={{display: "flex", flexDirection: "row"}}>
                <div style={{flex: 9}}>
                    <div id={id}>
                        <Loading />
                    </div>
                    <DatasetTable />
                </div>
                {hasFilters ? (
                    <div
                        style={{
                            marginLeft: 10,
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
            show_tooltip: settings.show_tooltip,
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
                .catch(error => {
                    callback({error});
                })
                .then(callback);
        }
    }

    displayAsPage($el, options) {
        options = options || {};

        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            callback = resp => {
                if (window.isEditable) {
                    title.append(this.addActionsMenu());
                }
                if (resp.dataset) {
                    const settings = this.getSettings(),
                        dataset = resp.dataset;

                    $el.empty().append($plotDiv);
                    if (!options.visualOnly) {
                        $el.prepend(title).append(captionDiv);
                    }

                    startupHeatmapAppRender($plotDiv[0], settings, dataset, options);

                    if (options.cb) {
                        options.cb(this);
                    }

                    caption.renderAndEnable();
                } else if (resp.error) {
                    $el.empty()
                        .prepend(title)
                        .append(this.getErrorDiv());
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
                if (resp.error) {
                    const settings = this.getSettings(),
                        dataset = resp.dataset;

                    modal.getModal().on("shown", function() {
                        startupHeatmapAppRender($plotDiv[0], settings, dataset, options);
                        caption.renderAndEnable();
                    });

                    modal
                        .addHeader($("<h4>").text(this.data.title))
                        .addBody([$plotDiv, captionDiv])
                        .addFooter("")
                        .show({maxWidth: 1200});
                } else if (resp.error) {
                    modal
                        .addHeader($("<h4>").text(this.data.title))
                        .addBody(this.getErrorDiv())
                        .addFooter("")
                        .show({maxWidth: 1200});
                } else {
                    throw "Unknown status.";
                }
            };

        options = options || {};
        this.getDataset(callback);
    }

    getErrorDiv() {
        return `<div class="alert alert-danger" role="alert">
            <i class="fa fa-exclamation-circle"></i>&nbsp;An error occurred; please modify settings...
        </div>`;
    }
}

export default ExploreHeatmap;
