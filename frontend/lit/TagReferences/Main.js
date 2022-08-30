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
            <div className="row mb-3">
                <div className="col-md-3">
                    <ReferenceSortSelector onChange={store.sortReferences} />
                    <h4>References</h4>
                    <div className="input-group mb-2 mt-1">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Search by Title/Abstract"></input>
                        <div className="input-group-append">
                            <button className="btn btn-primary" type="button">
                                <i className="fa fa-search" aria-hidden="true"></i>
                            </button>
                        </div>
                    </div>
                    <div className="card">
                        <div className="card-header p-2">
                            <button
                                className="btn btn-link"
                                data-toggle="collapse"
                                data-target="#taggedRefList">
                                Tagged
                            </button>
                        </div>
                        <div
                            id="taggedRefList"
                            className="show card-body ref-container px-1 resize-y"
                            style={{minHeight: "10vh", height: anyTagged ? "40vh" : "10vh"}}>
                            {store.referencesTagged.map(ref => (
                                <p
                                    key={ref.data.pk}
                                    className={
                                        ref.data.pk === selectedReferencePk
                                            ? "reference selected"
                                            : "reference"
                                    }
                                    onClick={() => store.changeSelectedReference(ref)}>
                                    {ref.shortCitation()}
                                </p>
                            ))}
                        </div>
                    </div>
                    <div className="card mt-3">
                        <div className="card-header p-2">
                            <button
                                className="btn btn-link"
                                data-toggle="collapse"
                                data-target="#untaggedRefList">
                                Untagged
                            </button>
                        </div>
                        <div
                            id="untaggedRefList"
                            className="show card-body px-1 resize-y"
                            style={{minHeight: "10vh", height: anyUntagged ? "40vh" : "10vh"}}>
                            {store.referencesUntagged.map(ref => (
                                <p
                                    key={ref.data.pk}
                                    className={
                                        ref.data.pk === selectedReferencePk
                                            ? "reference selected"
                                            : "reference"
                                    }
                                    onClick={() => store.changeSelectedReference(ref)}>
                                    {ref.shortCitation()}
                                </p>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    {store.selectedReference ? (
                        <div>
                            <h4>Tags for current reference</h4>
                            <div className="well" style={{minHeight: "50px"}}>
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
                            <div style={{paddingBottom: "1em"}}>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => store.saveAndNext()}>
                                    Save and go to next untagged
                                </button>
                                <span>&nbsp;</span>
                                <button
                                    className="btn btn-light"
                                    onClick={() => store.removeAllTags()}>
                                    Remove all tags
                                </button>
                                <span
                                    ref={this.savedPopup}
                                    className="btn litSavedIcon"
                                    style={{display: "none"}}>
                                    Saved!
                                </span>
                                <a
                                    className="btn btn-light float-right"
                                    rel="noopener noreferrer"
                                    target="_blank"
                                    href={store.selectedReference.get_edit_url()}
                                    title="Cleanup imported reference details">
                                    Edit
                                </a>
                            </div>
                            <Reference
                                reference={store.selectedReference}
                                showActions={false}
                                showHr={false}
                                showTags={false}
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
                <div className="col-md-3">
                    <h4>Available tags</h4>
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
