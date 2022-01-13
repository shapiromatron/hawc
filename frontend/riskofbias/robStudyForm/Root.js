import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Completeness from "./Completeness";
import Domain from "./Domain";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchFormData();
    }

    render() {
        let {store} = this.props;
        if (store.dataLoaded === false) {
            return <Loading />;
        }

        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={store.error} />
                <form>
                    {store.domainIds.map(domainId => {
                        return <Domain key={domainId} domainId={domainId} />;
                    })}
                    <div className="well">
                        <Completeness number={store.numIncompleteScores} />
                        <button
                            className="btn btn-primary space"
                            type="button"
                            onClick={store.submitScores}>
                            Save changes
                        </button>
                        <button className="ml-3 btn btn-light" onClick={store.cancelSubmitScores}>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
