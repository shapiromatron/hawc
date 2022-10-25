import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import Reference from "../components/Reference";
import ReferenceSortSelector from "../components/ReferenceSortSelector";
import TagTree from "../components/TagTree";
import HelpTextPopup from "shared/components/HelpTextPopup";

@inject("store")
@observer
class TagReferencesMain extends Component {
    constructor(props) {
        super(props);
        this.savedPopup = React.createRef();
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
            selectedReferenceTags = store.selectedReferenceTags ? store.selectedReferenceTags : [];
        return (
            <div className="row">
                <div className={store.filterClass} id="refFilter">
                    <div className="row px-3 justify-content-between" style={{maxHeight: "1.9rem"}}>
                        <h4 className="pt-2 mb-1">References</h4>
                        <ReferenceSortSelector onChange={store.sortReferences} />
                    </div>
                    <div className="card">
                        <div
                            id="fullRefList"
                            className="show card-body ref-container px-1 resize-y"
                            style={{minHeight: "10vh", height: "70vh"}}>
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
                                    {ref.tags.length > 0 ? (
                                        <i
                                            className="fa fa-tags"
                                            title="tagged"
                                            aria-hidden="true"></i>
                                    ) : null}
                                </p>
                            ))}
                        </div>
                    </div>
                </div>
                <div className={store.filterClass} id="taggingCol">
                    {store.selectedReference ? (
                        <div>
                            <div className="d-flex justify-content-between">
                                <h4 className="pt-2 my-0">
                                    <button
                                        id="collapse-btn"
                                        className="btn btn-sm btn-info"
                                        type="button"
                                        onClick={() => store.toggleSlideAway()}>
                                        <div className={store.filterClass} id="filter-btn">
                                            <i
                                                id="caret-left"
                                                className="fa fa-caret-left "
                                                aria-hidden="true"></i>
                                            &nbsp;
                                            <i className="fa fa-list-ul" aria-hidden="true"></i>
                                            &nbsp;
                                        </div>
                                    </button>
                                    &nbsp; Currently Applied Tags
                                    <HelpTextPopup
                                        title={""}
                                        content={"Click on a tag to remove"}
                                    />
                                </h4>
                                <span>&nbsp;</span>
                                <span
                                    ref={this.savedPopup}
                                    className="alert alert-success litSavedIcon"
                                    style={{display: "none"}}>
                                    Saved!
                                </span>
                                <button
                                    className="btn btn-primary align-self-end pt-1"
                                    onClick={() => store.saveAndNext()}>
                                    Save and go to next
                                </button>
                            </div>
                            <div className="well" style={{minHeight: "50px"}}>
                                {selectedReferenceTags.map((tag, i) => (
                                    <span
                                        key={i}
                                        title={tag.get_full_name()}
                                        className="refTag refTagEditing"
                                        onClick={() => store.removeTag(tag)}>
                                        {store.showFullTag ? tag.get_full_name() : tag.data.name}
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
                                extraActions={[
                                    <div
                                        className="dropdown-item"
                                        key={3}
                                        onClick={() => store.removeAllTags()}>
                                        &nbsp;Remove all tags
                                    </div>,
                                    <div
                                        className="dropdown-item"
                                        key={4}
                                        onClick={() => store.toggleFullTag()}>
                                        &nbsp;{store.showFullTag ? "Hide" : "Show"} full tag
                                    </div>,
                                ]}
                            />
                        </div>
                    ) : (
                        <h4>Select a reference</h4>
                    )}
                </div>
                <div className="px-3" id="tagtree-col">
                    <h4 className="pt-2">Available tags</h4>
                    <TagTree
                        tagtree={toJS(store.tagtree)}
                        handleTagClick={tag => store.addTag(tag)}
                    />
                    <div className="alert alert-info mt-3">
                        <b>Screening Instructions:</b>
                        <button type="button" className="close" data-dismiss="alert">
                            &times;
                        </button>
                        {store.config.instructions}
                    </div>
                </div>
            </div>
        );
    }
}

TagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default TagReferencesMain;
