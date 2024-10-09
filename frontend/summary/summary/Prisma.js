import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import Loading from "shared/components/Loading";

import $ from "$";

import {handleVisualError} from "./common";
import PrismaDatastore from "./prisma/PrismaDatastore";
import PrismaPlot from "./PrismaPlot";

const startupPrismaAppRender = function(el, settings, data, options) {
    const store = new PrismaDatastore(settings, data, options);

    if (options.asComponent) {
        return <PrismaComponent store={store} options={options} />;
    }

    try {
        ReactDOM.render(<PrismaComponent store={store} options={options} />, el);
    } catch (err) {
        handleVisualError(err, $(el));
    }
};

@observer
class PrismaComponent extends Component {
    componentDidMount() {
        const {store} = this.props,
            id = store.settingsHash,
            el = document.getElementById(id);

        if (el) {
            new PrismaPlot(store, this.props.options).render(el);
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
    options: PropTypes.object.isRequired,
};

export default startupPrismaAppRender;
