import $ from "jquery";
import _ from "lodash";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component, useEffect} from "react";
import Alert from "shared/components/Alert";
import HelpTextPopup from "shared/components/HelpTextPopup";
import Modal from "shared/components/Modal";
import HAWCUtils from "shared/utils/HAWCUtils";
import {LocalStorageBoolean} from "shared/utils/LocalStorage";

import Reference from "../components/Reference";
import TagTree from "../components/TagTree";

@inject("store")
@observer
class ReferenceListItem extends Component {
    render() {
        const {store, reference, selectedReferencePk} = this.props,
            isSelected = reference.data.pk === selectedReferencePk,
            divClass = `d-flex justify-content-between align-items-center reference ${
                isSelected ? "selected" : ""
            }`,
            title = store.config.conflict_resolution ? "has consensus tag(s)" : "tagged";

        return (
            <div className={divClass} onClick={() => store.setReference(reference)}>
                <p className="mb-0 pr-1">{reference.shortCitation()}</p>
                <div className="mr-1 d-flex" style={{flexWrap: "nowrap"}}>
                    {store.config.conflict_resolution && reference.userTags ? (
                        <i
                            className="fa fa-fw fa-tags small-tag-icon user"
                            style={{margin: "0.1rem"}}
                            title={"has tags from you"}
                            aria-hidden="true"></i>
                    ) : null}
                    {reference.tags.length > 0 ? (
                        <i
                            className="fa fa-fw fa-tags small-tag-icon consensus"
                            style={{margin: "0.1rem"}}
                            title={title}
                            aria-hidden="true"></i>
                    ) : null}
                </div>
            </div>
        );
    }
}
ReferenceListItem.propTypes = {
    reference: PropTypes.object.isRequired,
    selectedReferencePk: PropTypes.number.isRequired,
    store: PropTypes.object,
};

var ReferenceUDF = inject("store")(
    observer(({currentUDF, UDFValues, UDFError}) => {
        useEffect(() => {
            // clear the entire form of existing data
            $("#udf-form :input").each(function() {
                switch ($(this).prop("type")) {
                    case "radio":
                    case "checkbox":
                        $(this).attr("checked", false);
                        break;
                    default:
                        $(this).val("");
                }
            });
            // add data for current tags/reference
            _.forEach(UDFValues, function(value, name) {
                _.forEach(value, function(val) {
                    var input = $(`[name="${name}"]`);
                    if (input.prop("multiple")) {
                        input.children(`option[value="${val}"]`).prop("selected", true);
                    } else {
                        switch (input.prop("type")) {
                            case "radio":
                            case "checkbox":
                                input.each(function() {
                                    // multiple select checkbox
                                    if ($(this).attr("value") == val) {
                                        $(this).attr("checked", val);
                                    }
                                    // single checkbox
                                    else if (
                                        $(this).attr("value") == undefined &&
                                        (val == "on" || val == true)
                                    ) {
                                        $(this).attr("checked", true);
                                    }
                                });
                                break;
                            default:
                                // text/number fields
                                input.val(val);
                        }
                    }
                });
            });
            HAWCUtils.dynamicFormListeners();
            $("#udf-form .invalid-feedback").remove();
            $("#udf-form .is-invalid").removeClass("is-invalid");
            $("#udf-form .bg-pink").removeClass("bg-pink");
            _.forEach(_.fromPairs(UDFError), function(error, field) {
                var input = $(`[name="${field}"]`);
                input.addClass("is-invalid");
                input
                    .closest("div.form-group")
                    .append(`<div class="invalid-feedback d-block">${error.join(" ")}</div>`);
                input
                    .closest('[id^="collapse-"]')
                    .siblings('[id^="udf-header-"]')
                    .addClass("bg-pink");
            });
        });

        return currentUDF.length > 0 ? (
            <form id="udf-form">
                <div dangerouslySetInnerHTML={{__html: currentUDF}} />
            </form>
        ) : (
            ""
        );
    })
);

ReferenceUDF.propTypes = {
    currentUDF: PropTypes.string.isRequired,
    UDFValues: PropTypes.object.isRequired,
    UDFError: PropTypes.array,
};

@inject("store")
@observer
class TagReferencesMain extends Component {
    constructor(props) {
        super(props);
        this.showFullTag = new LocalStorageBoolean("lit-showFullTag", true);
        this.pinInstructions = new LocalStorageBoolean("lit-pinInstructions", false);
        this.expandAbstract = new LocalStorageBoolean("lit-expandAbstract", true);
        this.state = {
            showFullTag: this.showFullTag.value,
            pinInstructions: this.pinInstructions.value,
            expandAbstract: this.expandAbstract.value,
        };
    }
    render() {
        const {store} = this.props,
            {
                hasReference,
                reference,
                referenceTags,
                referenceUserTags,
                currentUDF,
                UDFValues,
                UDFError,
            } = store,
            selectedReferencePk = hasReference ? reference.data.pk : -1; // -1 will never match

        return (
            <div className="row">
                <div className={store.filterClass} id="refFilter">
                    <div
                        className="row px-3 mb-2 justify-content-between"
                        style={{maxHeight: "1.9rem"}}>
                        <h4>References</h4>
                    </div>
                    <div className="card">
                        <div
                            id="fullRefList"
                            className="show card-body ref-container px-0 py-1 resize-y"
                            style={{height: "50rem"}}>
                            {store.references.map(reference => {
                                return (
                                    <ReferenceListItem
                                        key={reference.data.pk}
                                        reference={reference}
                                        selectedReferencePk={selectedReferencePk}
                                    />
                                );
                            })}
                        </div>
                    </div>
                </div>
                <div className={store.filterClass} id="taggingCol">
                    {store.hasReference ? (
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
                                <button
                                    className="btn btn-primary pt-1"
                                    title="Save and go to next reference"
                                    onClick={() => store.saveAndNext()}>
                                    <i className="fa fa-save"></i>&nbsp;Save and next
                                </button>
                            </div>
                            {store.errorOnSave ? (
                                <Alert
                                    className="alert-danger mt-2"
                                    message={
                                        store.UDFError
                                            ? "An error was found with your tag form data."
                                            : "An error occurred in saving; please wait a moment and retry. If the error persists please contact HAWC staff."
                                    }
                                />
                            ) : null}
                            <div className="well" style={{minHeight: "50px"}}>
                                {store.successMessage ? (
                                    <Alert
                                        className="alert-success fade-in-out"
                                        icon="fa-check-square"
                                        message={store.successMessage}
                                    />
                                ) : (
                                    <>
                                        {referenceTags.map((tag, i) => (
                                            <span
                                                key={i}
                                                title={
                                                    store.config.conflict_resolution
                                                        ? "Tag: ".concat(tag.get_full_name())
                                                        : tag.get_full_name()
                                                }
                                                className={
                                                    store.hasTag(referenceUserTags, tag)
                                                        ? "refTag cursor-pointer"
                                                        : "refTag refUserTagRemove cursor-pointer"
                                                }
                                                onClick={() => store.toggleTag(tag)}>
                                                {this.state.showFullTag
                                                    ? tag.get_full_name()
                                                    : tag.data.name}
                                            </span>
                                        ))}
                                        {referenceUserTags
                                            .filter(tag => !store.hasTag(referenceTags, tag))
                                            .map((tag, i) => (
                                                <span
                                                    key={i}
                                                    title={"Proposed: ".concat(tag.get_full_name())}
                                                    className="refTag refUserTag cursor-pointer"
                                                    onClick={() => store.removeTag(tag)}>
                                                    {this.state.showFullTag
                                                        ? tag.get_full_name()
                                                        : tag.data.name}
                                                </span>
                                            ))}
                                    </>
                                )}
                            </div>
                            <Reference
                                reference={reference}
                                keywordDict={store.config.keywords}
                                showActions={false}
                                showHr={false}
                                showTags={false}
                                showActionsTagless={true}
                                actionsBtnClassName={"btn-sm btn-secondary"}
                                expanded={this.expandAbstract.value}
                                extraActions={[
                                    <div
                                        className="dropdown-item cursor-pointer"
                                        key={4}
                                        onClick={() => store.removeAllTags()}>
                                        &nbsp;Remove all tags
                                    </div>,
                                    <div
                                        className="dropdown-item cursor-pointer"
                                        key={5}
                                        onClick={() => {
                                            this.showFullTag.toggle();
                                            this.setState({showFullTag: this.showFullTag.value});
                                        }}>
                                        &nbsp;
                                        {this.state.showFullTag
                                            ? "Show collapsed tag"
                                            : "Show full tag"}
                                    </div>,
                                    <div
                                        className="dropdown-item cursor-pointer"
                                        key={6}
                                        onClick={() => {
                                            this.expandAbstract.toggle();
                                            this.setState({
                                                expandAbstract: this.expandAbstract.value,
                                            });
                                        }}>
                                        &nbsp;
                                        {this.state.expandAbstract
                                            ? "Use collapsed view"
                                            : "Use expanded view"}
                                    </div>,
                                    store.config.instructions.length > 0 ? (
                                        <div
                                            className="dropdown-item cursor-pointer"
                                            key={7}
                                            onClick={() => store.setInstructionsModal(true)}>
                                            &nbsp;View instructions
                                        </div>
                                    ) : null,
                                ]}
                            />
                            <ReferenceUDF
                                currentUDF={currentUDF}
                                UDFValues={UDFValues}
                                UDFError={UDFError}
                            />
                        </div>
                    ) : (
                        <h4>Select a reference</h4>
                    )}
                    {selectedReferencePk === -1 ? (
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
                        showTagHoverAdd={true}
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
