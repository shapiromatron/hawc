import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {createRoot} from "react-dom/client";
import Loading from "shared/components/Loading";
import h from "shared/utils/helpers";

import $ from "$";

import PrismaPlot from "./PrismaPlot";
import {handleVisualError} from "./common";
import PrismaDatastore from "./prisma/PrismaDatastore";

const startupPrismaAppRender = function (el, settings, data, config, asComponent = false) {
        if (_.isUndefined(data)) {
            if (asComponent == true) {
                console.error("Cannot return asComponent if we have to fetch data");
            }
            fetch(config.api_data_url, h.fetchGet)
                .then(resp => resp.json())
                .then(data => start(el, settings, data, config, asComponent));
        } else {
            return start(el, settings, data, config, asComponent);
        }
    },
    start = function (el, settings, data, config, asComponent) {
        const store = new PrismaDatastore(settings, data, config);
        if (asComponent) {
            return <PrismaComponent store={store} config={config} />;
        }
        try {
            const root = createRoot(el);
            root.render(<PrismaComponent store={store} config={config} />);
        } catch (err) {
            handleVisualError(err, $(el));
        }
    };

@observer
class PrismaComponent extends Component {
    componentDidMount() {
        const {store, config} = this.props,
            id = store.settingsHash,
            el = document.getElementById(id);

        if (el) {
            new PrismaPlot(store, config).render(el);
        }
    }
    render() {
        const {store} = this.props,
            id = store.settingsHash;
        return (
            <div className="row py-3">
                <div id={id} className="col-lg-8">
                    <Loading />
                </div>
                <div id={`${id}-prisma-reference-list`} className="col-lg-4"></div>
            </div>
        );
    }
}
PrismaComponent.propTypes = {
    store: PropTypes.object.isRequired,
    config: PropTypes.object.isRequired,
};

export default startupPrismaAppRender;
