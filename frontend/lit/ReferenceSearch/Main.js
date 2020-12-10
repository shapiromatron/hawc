import React, {Component} from "react";
import PropTypes from "prop-types";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import ReferenceTable from "../components/ReferenceTable";
import SearchForm from "./SearchForm";

@inject("store")
@observer
class ReferenceSearchMain extends Component {
    render() {
        const {store} = this.props,
            {isSearching, references, hasReferences, numReferences} = store;
        return (
            <div className="container-fluid">
                <div className="card">
                    <div className="card-header">
                        <button
                            className="btn btn-link"
                            data-toggle="collapse"
                            data-target="#searchCollapser">
                            Find references
                        </button>
                    </div>
                    <div id="searchCollapser" className="collapse show">
                        <div className="card-body">
                            <SearchForm />
                        </div>
                    </div>
                </div>
                <div>
                    {isSearching ? <Loading /> : null}
                    {hasReferences && numReferences === 0 ? (
                        <p>Search found no references; please change query parameters.</p>
                    ) : null}
                    {numReferences > 0 ? (
                        numReferences === store.MAX_REFERENCES ? (
                            <p>
                                <b>Showing the first {numReferences} references.</b>
                            </p>
                        ) : (
                            <p>
                                <b>{numReferences} references found.</b>
                            </p>
                        )
                    ) : null}
                    {hasReferences && numReferences > 0 ? (
                        <ReferenceTable references={toJS(references)} showActions={false} />
                    ) : null}
                </div>
            </div>
        );
    }
}

ReferenceSearchMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceSearchMain;
