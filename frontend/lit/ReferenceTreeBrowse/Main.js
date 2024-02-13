import TagActions from "lit/components/TagActions";
import _ from "lodash";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import LabelInput from "shared/components/LabelInput";
import Loading from "shared/components/Loading";
import Paginator from "shared/components/Paginator";
import TextInput from "shared/components/TextInput";

import ReferenceSortSelector from "../components/ReferenceSortSelector";
import TagTree from "../components/TagTree";
import ReferenceTableMain from "./ReferenceTableMain";
import YearHistogram from "./YearHistogram";

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
            {
                selectedReferences,
                selectedReferencesLoading,
                filteredReferences,
                paginatedReferences,
                yearFilter,
                page,
                fetchPage,
            } = store,
            yearText = yearFilter ? ` (${yearFilter.min}-${yearFilter.max})` : "";

        return (
            <div className="row">
                <div className="col-md-12 pb-3">
                    {store.untaggedReferencesSelected === true ? (
                        <h3>Untagged references</h3>
                    ) : store.selectedTag === null ? (
                        <h3>Available references</h3>
                    ) : (
                        <div className="d-flex">
                            <h3 className="mb-0 align-self-center">
                                <span>
                                    {selectedReferences && selectedReferences.length > 0
                                        ? `${filteredReferences.length} references tagged:`
                                        : "References tagged:"}
                                </span>
                            </h3>
                            <span className="mb-0 ml-2 refTag">
                                {store.selectedTag.get_full_name()}
                            </span>
                            <span>{yearText}</span>
                            <TagActions
                                assessmentId={store.config.assessment_id}
                                tagId={store.selectedTag ? store.selectedTag.data.pk : undefined}
                                untagged={store.untaggedReferencesSelected}
                                canEdit={store.config.canEdit}
                            />
                        </div>
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
                            <ReferenceSortSelector onChange={store.sortReferences} />
                            <QuickSearch
                                updateQuickFilter={text => store.changeQuickFilterText(text)}
                            />
                            <LabelInput
                                label={`Showing ${paginatedReferences.length} of ${selectedReferences.length}:`}
                            />
                            <div id="reference-list" className="list-group">
                                {paginatedReferences.map(referenceListItem)}
                                <span className="mt-3"></span>
                                {page ? <Paginator page={page} onChangePage={fetchPage} /> : null}
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
                        untaggedHandleClick={store.handleUntaggedReferenceClick}
                        untaggedCount={store.config.untaggedReferenceCount}
                        untaggedReferencesSelected={store.untaggedReferencesSelected}
                    />
                </div>
            </div>
        );
    }
}

ReferenceTreeMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceTreeMain;
