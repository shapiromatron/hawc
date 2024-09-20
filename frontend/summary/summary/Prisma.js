import BaseVisual from "./BaseVisual";
import PrismaDatastore from "./prisma/PrismaDatastore";
import { inject, observer, Provider } from "mobx-react";
import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import $ from "$";

import { handleVisualError } from "./common";
import { NULL_VALUE } from "./constants";

const startupPrismaAppRender = function (el, settings, datastore, options) {

    const store = new PrismaDatastore(settings, datastore, options);
    try {
        if (store.withinRenderableBounds) {
            store.initialize();
        }
        ReactDOM.render(
            <Provider store={store}>
                <PrismaComponent options={options} />
            </Provider>,
            el
        );
    } catch (err) {
        handleVisualError(err, $(el));
    }
};

@inject("store")
@observer
class PrismaComponent extends Component {
    componentDidMount() {
        const { store } = this.props,
            id = store.settingsHash,
            el = document.getElementById(id);

        if (el) {
            new PrismaPlot(store, this.props.options).render(el, tooltipEl);
        }
    }
    render() {
        const { store } = this.props,
            id = store.settingsHash,
            hasFilters = store.settings.filter_widgets.length > 0;

        if (!store.hasDataset) {
            return <Alert message={"No data are available."} />;
        }

        if (!store.withinRenderableBounds) {
            return <Alert message={`This Prisma visual is too large and cannot be rendered.`} />;
        }

        return (
            <>
                <div style={{ display: "flex", flexDirection: "row" }}>
                    <div style={{ flex: 9 }}>
                        <div id={id}>
                            <Loading />
                        </div>
                    </div>
                    <div id={`tooltip-${id}`} style={{ position: "absolute" }}></div>
                </div>
            </>
        );
    }
}
PrismaComponent.propTypes = {
    store: PropTypes.object,
    options: PropTypes.object.isRequired,
};


class Prisma extends BaseVisual {
    constructor(data, dataset) {
        super(data);
        this.dataset = {data: 1};
    }

    getDataset(callback) {
        callback({dataset: this.dataset});
    }
    displayAsPage($el, options) {
        var $plotDiv = $("<div>"),
        callback = resp => {
            if (resp.dataset || resp.error) {
                // exit early if we got an error
                if (resp.error) {
                    HAWCUtils.addAlert(resp.error, $plotDiv);
                    $el.empty().append($plotDiv);
                    return;
                }
                try {
                    $el.empty().append($plotDiv);
                    startupPrismaAppRender($plotDiv[0], {}, {}, {});
                } catch(err) {
                    return handleVisualError(err, $plotDiv);
                }

            } else {
                throw "Unknown status.";
            }
        };

        this.getDataset(callback);
    }

    displayAsModal(options) {}
}

export default Prisma;
