import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import Reference from "../components/Reference";
import ReferenceSortSelector from "../components/ReferenceSortSelector";
import TagTree from "../components/TagTree";
import HelpTextPopup from "shared/components/HelpTextPopup";
import Modal from "shared/components/Modal";
import {LocalStorageBoolean} from "shared/utils/LocalStorage";

@inject("store")
@observer
class TagReferencesMain extends Component {
    constructor(props) {
        super(props);
        this.savedPopup = React.createRef();
        this.showFullTag = new LocalStorageBoolean("lit-showFullTag", true);
        this.pinInstructions = new LocalStorageBoolean("lit-pinInstructions", false);
        this.state = {
            showFullTag: this.showFullTag.value,
            pinInstructions: this.pinInstructions.value,
        };
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
                    <div
                        className="row px-3 mb-2 justify-content-between"
                        style={{maxHeight: "1.9rem"}}>
                        <h4>References</h4>
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
                                <h4 className="my-0">
                                    <button
                                        id="collapse-btn"
                                        className="btn btn-sm btn-info"
                                        title="Show/hide reference sidebar"
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
                                <span
                                    ref={this.savedPopup}
                                    className="bg-success text-white font-weight-bold px-2 rounded"
                                    style={{display: "none"}}>
                                    Saved!
                                </span>
                                <button
                                    className="btn btn-primary pt-1"
                                    title="Save and go to next reference"
                                    onClick={() => store.saveAndNext()}>
                                    <i className="fa fa-save"></i>&nbsp;Save and next
                                </button>
                            </div>
                            <div className="well" style={{minHeight: "50px"}}>
                                {selectedReferenceTags.map((tag, i) => (
                                    <span
                                        key={i}
                                        title={tag.get_full_name()}
                                        className="refTag refTagEditing"
                                        onClick={() => store.removeTag(tag)}>
                                        {this.state.showFullTag
                                            ? tag.get_full_name()
                                            : tag.data.name}
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
                                keywordDict={store.config.keywords}
                                showActions={false}
                                showHr={false}
                                showTags={false}
                                showActionsTagless={true}
                                actionsBtnClassName={"btn-sm btn-secondary"}
                                extraActions={[
                                    <div
                                        className="dropdown-item cursor-pointer"
                                        key={3}
                                        onClick={() => store.removeAllTags()}>
                                        &nbsp;Remove all tags
                                    </div>,
                                    <div
                                        className="dropdown-item cursor-pointer"
                                        key={4}
                                        onClick={() => {
                                            this.showFullTag.toggle();
                                            this.setState({showFullTag: this.showFullTag.value});
                                        }}>
                                        &nbsp;
                                        {this.state.showFullTag
                                            ? "Show collapsed tag"
                                            : "Show full tag"}
                                    </div>,
                                    store.config.instructions.length > 0 ? (
                                        <div
                                            className="dropdown-item cursor-pointer"
                                            key={5}
                                            onClick={() => store.setInstructionsModal(true)}>
                                            &nbsp;View instructions
                                        </div>
                                    ) : null,
                                ]}
                            />
                        </div>
                    ) : (
                        <h4>Select a reference</h4>
                    )}
                    {selectedReferencePk === null ? (
                        <div className="alert alert-danger">No references found.</div>
                    ) : null}
                    {this.state.pinInstructions && store.config.instructions.length > 0 ? (
                        <div
                            className="alert alert-info mt-3 resize-y"
                            style={
                                store.config.instructions.length > 1000 ? {height: "30vh"} : null
                            }>
                            <b>Screening Instructions:</b>
                            <button
                                type="button"
                                className="close"
                                onClick={() => {
                                    this.pinInstructions.set(false);
                                    this.setState({pinInstructions: false});
                                }}>
                                &times;
                            </button>
                            <div dangerouslySetInnerHTML={{__html: store.config.instructions}} />
                        </div>
                    ) : null}
                </div>
                <div className="px-3 w-25">
                    <h4>Available tags</h4>
                    <TagTree
                        tagtree={toJS(store.tagtree)}
                        handleTagClick={tag => store.addTag(tag)}
                        showTagHover={true}
                    />
                </div>
                <Modal
                    isShown={store.showInstructionsModal && store.config.instructions.length > 0}
                    onClosed={() => store.setInstructionsModal(false)}>
                    <div className="modal-header pb-0">
                        <h4>
                            Screening Instructions
                            <button
                                type="button"
                                title={
                                    this.state.pinInstructions ? "Unpin from page" : "Pin to page"
                                }
                                className="btn btn-sm btn-info ml-3"
                                onClick={() => {
                                    this.pinInstructions.toggle();
                                    this.setState({pinInstructions: this.pinInstructions.value});
                                    store.setInstructionsModal(false);
                                }}>
                                <i className="fa fa-thumb-tack" aria-hidden="true"></i>
                            </button>
                        </h4>
                        <button
                            type="button"
                            className="float-right close"
                            onClick={() => store.setInstructionsModal(false)}
                            aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div
                        className="modal-body"
                        dangerouslySetInnerHTML={{__html: store.config.instructions}}
                    />
                </Modal>
            </div>
        );
    }
}

TagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default TagReferencesMain;
