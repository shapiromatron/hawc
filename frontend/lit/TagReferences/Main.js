import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import Reference from "../components/Reference";
import ReferenceSortSelector from "../components/ReferenceSortSelector";
import TagTree from "../components/TagTree";

@inject("store")
@observer
class TagReferencesMain extends Component {
    constructor(props) {
        super(props);
        this.savedPopup = React.createRef();
        this.state = {
            filterClass: '',
        }
        this.filterClicked = this.filterClicked.bind(this);
    }

    filterClicked() {
        if (this.state.filterClass === '') {
            this.setState({
                filterClass: 'slideAway',
            })
        }
        else {
            this.setState({
                filterClass: '',
            })
        }

    }
    _setSaveIndicator() {
        const el = this.savedPopup.current;
        if (el) {
            this.props.store.setSaveIndicatorElement(el);
        }
    }
    componentDidMount() {
        this._setSaveIndicator();
    }
    componentDidUpdate() {
        this._setSaveIndicator();
    }
    render() {
        const {store} = this.props,
            selectedReferencePk = store.selectedReference ? store.selectedReference.data.pk : null,
            selectedReferenceTags = store.selectedReferenceTags ? store.selectedReferenceTags : [],
            allTagged = store.referencesUntagged.length == 0,
            anyTagged = store.referencesTagged.length > 0,
            anyUntagged = store.referencesUntagged.length > 0;
        return (
            <div className="row">
                <div className={this.state.filterClass} id="refFilter">
                    <div className="row px-3 justify-content-between">
                        <h4 className="pt-2 mb-1">
                            References
                        </h4>
                        <ReferenceSortSelector onChange={store.sortReferences} />
                    </div>
                    <div className="card">
                        <div
                            id="fullRefList"
                            className="show card-body ref-container px-1 resize-y"
                            style={{ minHeight: "10vh", height: "70vh" }}>
                            {store.references.map(ref => (
                                <p
                                    key={ref.data.pk}
                                    className={
                                        ref.data.pk === selectedReferencePk
                                            ? "reference selected"
                                            : "reference"
                                    }
                                    onClick={() => store.changeSelectedReference(ref)}>
                                    {ref.shortCitation()}&nbsp;
                                    {ref.tags.length > 0 ? <i class="fa fa-tags" title="tagged" aria-hidden="true"></i> : null}
                                </p>
                            ))}
                        </div>
                    </div>
                </div>
                <div className={this.state.filterClass} id="taggingCol">
                    {store.selectedReference ? (
                        <div>
                            <div className="d-flex justify-content-between">
                                <h4 className="pt-2 my-0">
                                    <button id="collapse-btn" className="btn btn-sm btn-info" type="button" onClick={this.filterClicked}>
                                        <div className={this.state.filterClass} id="filter-btn">
                                            <i id="caret-left" className="fa fa-caret-left " aria-hidden="true"></i>&nbsp;
                                            <i className="fa fa-list-ul" aria-hidden="true"></i>&nbsp;
                                        </div>
                                    </button>
                                    &nbsp;
                                    Currently Applied Tags
                                </h4>
                                <span>&nbsp;</span>
                                <span
                                    ref={this.savedPopup}
                                    className="alert alert-success litSavedIcon"
                                    style={{ display: "none" }}>
                                    Saved!
                                </span>
                                <div className="pt-1">
                                    <button
                                        className="btn btn-light mx-2 align-self-end"
                                        title="Remove all tags"
                                        onClick={() => store.removeAllTags()}>
                                        <i className="fa fa-times" aria-hidden="true"></i>
                                    </button>
                                    <button
                                        className="btn btn-primary align-self-end"
                                        onClick={() => store.saveAndNext()}>
                                        Save and go to next untagged
                                    </button>
                                </div>
                            </div>
                            <div className="well" style={{ minHeight: "50px" }}>
                                {selectedReferenceTags.map((tag, i) => (
                                    <span
                                        key={i}
                                        title="click to remove"
                                        className="refTag refTagEditing"
                                        onClick={() => store.removeTag(tag)}>
                                        {tag.get_full_name()}
                                    </span>
                                ))}
                            </div>
                            {store.errorOnSave ? (
                                <div className="alert alert-danger">
                                    An error occurred in saving; please wait a moment and retry. If
                                    the error persists please contact HAWC staff.
                                </div>
                            ) : null}
                            <Reference
                                reference={store.selectedReference}
                                showActions={false}
                                showHr={false}
                                showTags={false}
                                showActionsTagless={true}
                                actionsBtnClassName={"btn-sm btn-secondary"}
                            />
                        </div>
                    ) : (
                        <h4>Select a reference</h4>
                    )}
                    {selectedReferencePk === null && allTagged ? (
                        <div className="alert alert-success">
                            All references have been successfully tagged. Congratulations!
                        </div>
                    ) : null}
                </div>
                <div className="px-3" id="tagtree-col">
                    <h4 className="pt-2">Available tags</h4>
                    <TagTree
                        tagtree={toJS(store.tagtree)}
                        handleTagClick={tag => store.addTag(tag)}
                    />
                </div>
            </div>
        );
    }
}

TagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default TagReferencesMain;
