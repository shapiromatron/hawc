import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import Loading from "shared/components/Loading";
import TextInput from "shared/components/TextInput";
import TagTree from "../components/TagTree";
import YearHistogram from "./YearHistogram";
import ReferenceTableMain from "./ReferenceTableMain";

const referenceListItem = ref => {
    return (
        <a key={ref.data.pk} className="list-group-item" href={`#referenceId${ref.data.pk}`}>
            {ref.shortCitation()}
        </a>
    );
};

@observer
class QuickSearch extends Component {
    constructor(props) {
        super(props);
        this.state = {text: ""};
        this.updateQuery = _.debounce(() => props.updateQuickFilter(this.state.text), 200);
    }
    render() {
        return (
            <TextInput
                name="quickSearch"
                label="Quick search"
                value={this.state.text}
                helpText="Search by title, authors, year"
                onChange={e => {
                    const text = e.target.value;
                    this.setState({text});
                    this.updateQuery(text);
                }}
            />
        );
    }
}
QuickSearch.propTypes = {
    updateQuickFilter: PropTypes.func.isRequired,
};

@inject("store")
@observer
class ReferenceTreeMain extends Component {
    componentDidMount() {
        this.props.store.tryLoadTag();
    }
    render() {
        const {store} = this.props,
            actions = store.getActionLinks,
            {selectedReferences, selectedReferencesLoading, filteredReferences, yearFilter} = store,
            yearText = yearFilter ? ` (${yearFilter.min}-${yearFilter.max})` : "";

        return (
            <div className="row">
                <div className="col-md-12 pb-2">
                    {actions.length > 0 ? (
                        <div className="dropdown btn-group float-right">
                            <a className="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Actions
                            </a>
                            <div className="dropdown-menu dropdown-menu-right">
                                {actions.map((action, index) => (
                                    <a key={index} className="dropdown-item" href={action[0]}>
                                        {action[1]}
                                    </a>
                                ))}
                            </div>
                        </div>
                    ) : null}
                    {store.untaggedReferencesSelected === true ? (
                        <h4>Untagged references</h4>
                    ) : store.selectedTag === null ? (
                        <h4>Available references</h4>
                    ) : (
                        <h4>
                            <span>
                                {selectedReferences && selectedReferences.length > 0
                                    ? `${filteredReferences.length} references tagged:`
                                    : "References tagged:"}
                            </span>
                            <span className="ml-2 refTag">{store.selectedTag.get_full_name()}</span>
                            <span>{yearText}</span>
                        </h4>
                    )}
                </div>
                <div className="col-md-3">
                    {selectedReferencesLoading ? <Loading /> : null}
                    {selectedReferences && selectedReferences.length > 0 ? (
                        <>
                            <YearHistogram
                                references={selectedReferences}
                                yearFilter={store.yearFilter}
                                onFilter={store.updateYearFilter}
                            />
                            <QuickSearch
                                updateQuickFilter={text => store.changeQuickFilterText(text)}
                            />
                            <div
                                id="reference-list"
                                className="list-group"
                                style={{maxHeight: "50vh"}}>
                                {filteredReferences.map(referenceListItem)}
                            </div>
                        </>
                    ) : null}
                </div>
                <div className="col-md-6">
                    <div id="references_detail_div">
                        {store.selectedTag === null &&
                        store.untaggedReferencesSelected === false ? (
                            <p className="form-text text-muted">
                                Click on a tag to view tagged references.
                            </p>
                        ) : null}
                        <ReferenceTableMain />
                    </div>
                </div>
                <div className="col-md-3">
                    <TagTree
                        tagtree={toJS(store.tagtree)}
                        handleTagClick={tag => store.handleTagClick(tag)}
                        showReferenceCount={true}
                        selectedTag={store.selectedTag}
                    />
                    <br />
                    <p
                        className="nestedTag"
                        id="untaggedReferences"
                        onClick={() => store.handleUntaggedReferenceClick(null)}>
                        Untagged References: ({store.config.untaggedReferenceCount})
                    </p>
                </div>
            </div>
        );
    }
}

ReferenceTreeMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceTreeMain;
