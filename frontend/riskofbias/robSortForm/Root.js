import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Domain from "./Domain";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.setConfig("config");
        this.props.store.fetchRoBData();
    }

    render() {
        let {store} = this.props;
        if (store.dataLoaded === false) {
            return <Loading />;
        }

        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={store.error} />
                {store.domains.map((domain, domainIndex) => {
                    return <Domain key={domain.id} domainIndex={domainIndex} domain={domain} />;
                })}
                <button
                    className="btn btn-primary space"
                    type="button"
                    onClick={store.submitScores}>
                    Save changes
                </button>
                <button className="btn space" onClick={store.cancelSubmitScores}>
                    Cancel
                </button>
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
