import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import Completeness from "./Completeness";
import Domain from "./Domain";

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
                <form>
                    {store.domainIds.map(domainId => {
                        return <Domain key={domainId} domainId={domainId} />;
                    })}
                    <div className="well">
                        <Completeness number={store.numIncompleteScores} />
                        {store.changedSavedDiv ? (
                            <div className="alert alert-info">
                                <p className="mb-0">
                                    <i className="fa fa-save mr-2" />
                                    Changes saved!
                                </p>
                            </div>
                        ) : null}
                        <ScrollToErrorBox error={store.error} />
                        <div className="d-flex justify-content-between">
                            <button
                                className="btn btn-primary"
                                type="button"
                                onClick={() => store.submitScores(false)}>
                                Save and continue editing
                            </button>
                            <div>
                                <button
                                    className="btn btn-light mr-3"
                                    onClick={store.cancelSubmitScores}>
                                    Cancel
                                </button>
                                <button
                                    className="btn btn-primary"
                                    type="button"
                                    onClick={() => store.submitScores(true)}>
                                    Save and return
                                </button>
                            </div>
                        </div>
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
