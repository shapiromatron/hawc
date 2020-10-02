import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

import h from "textCleanup/utils/helpers";

@inject("store")
@observer
class App extends Component {
    componentDidMount() {
        this.props.store.loadAssessmentMetadata();
    }
    render() {
        const {store} = this.props;

        if (store.isLoading) {
            return <Loading />;
        }

        if (store.cleanupField) {
            return; // load field
        }

        if (store.cleanupModel) {
            return; // load model
        }

        // else load assessment root
        return (
            <div>
                <h2>Cleanup {store.assessmentMetadata.name}</h2>
                <p className="help-block">
                    After data has been initially extracted, this module can be used to update and
                    standardize text which was used during data extraction.
                </p>
                <b>To begin, select a data-type to cleanup</b>
                <ul>
                    {store.assessmentMetadata.items
                        .filter(d => d.count > 0)
                        .map(d => {
                            return (
                                <li key={d.type}>
                                    <a href="#" onClick={() => store.loadCleanupModel(d)}>
                                        {d.count}&nbsp;{d.title}
                                    </a>
                                </li>
                            );
                        })}
                </ul>
            </div>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
