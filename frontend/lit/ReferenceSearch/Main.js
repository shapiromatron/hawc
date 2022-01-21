import React, {Component} from "react";
import PropTypes from "prop-types";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";

import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import ReferenceTable from "../components/ReferenceTable";
import SearchForm from "./SearchForm";
import ReferenceSortSelector from "../components/ReferenceSortSelector";

@inject("store")
@observer
class ReferenceSearchMain extends Component {
    render() {
        const {store} = this.props,
            {
                isSearching,
                searchError,
                references,
                sortReferences,
                hasReferences,
                numReferences,
            } = store,
            nRefText =
                numReferences === store.MAX_REFERENCES ? (
                    <b>Showing the first {numReferences} references.</b>
                ) : (
                    <b>{numReferences} references found.</b>
                );

        return (
            <div className="container-fluid">
                <div className="card">
                    <div className="card-header">
                        <button
                            className="btn btn-link"
                            data-toggle="collapse"
                            data-target="#searchCollapser">
                            Search for references in this assessment
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
                    {searchError ? <Alert /> : null}
                    {hasReferences && numReferences === 0 ? (
                        <Alert
                            className="alert-info"
                            message="Search found no references; please change query parameters."
                        />
                    ) : null}
                    {numReferences > 0 ? (
                        <>
                            <ReferenceSortSelector onChange={sortReferences} />
                            <p>{nRefText}</p>
                        </>
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
