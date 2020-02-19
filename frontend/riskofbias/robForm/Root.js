import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Domain from "./Domain";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

@inject("store")
@observer
class Root extends Component {
    constructor(props) {
        super(props);
        /* TODO - remove state and move to store */
        this.state = {
            notesLeft: new Set(),
        };
    }

    componentDidMount() {
        this.props.store.setConfig("config");
        this.props.store.fetchFullStudy();
    }

    // handleUpdateNotes(id, action) {
    //     let notes = this.state.notesLeft;
    //     if (action === "clear") {
    //         notes.delete(id);
    //         this.setState({notesLeft: notes});
    //     } else if (action === "add") {
    //         notes.add(id);
    //         this.setState({notesLeft: notes});
    //     }
    // }

    render() {
        let store = this.props.store;
        if (store.dataLoaded === false) {
            return <Loading />;
        }

        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={store.error} />
                <form>
                    {store.domainIds.map(domainId => {
                        return (
                            <Domain
                                key={domainId}
                                domainId={domainId}
                                scores={store.getScoresForDomain(domainId)}
                            />
                        );
                    })}
                    {/* <Completeness number={this.state.notesLeft} /> */}
                    <button
                        className="btn btn-primary space"
                        type="button"
                        onClick={store.submitScores}>
                        Save changes
                    </button>
                    <button className="btn space" onClick={store.cancelSubmitScores}>
                        Cancel
                    </button>
                </form>
            </div>
        );
    }
}

Root.propTypes = {};

export default Root;
