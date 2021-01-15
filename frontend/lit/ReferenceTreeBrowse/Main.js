import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import ReferenceTable from "../components/ReferenceTable";
import TagTree from "../components/TagTree";
import YearHistogram from "./YearHistogram";
import Loading from "shared/components/Loading";

const referenceListItem = ref => {
    return (
        <a key={ref.data.pk} className="list-group-item" href={`#referenceId${ref.data.pk}`}>
            {ref.shortCitation()}
        </a>
    );
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
            {selectedReferences, selectedReferencesLoading} = store,
            {canEdit} = store.config;

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
                        <h3>Untagged references</h3>
                    ) : store.selectedTag === null ? (
                        <h3>Available references</h3>
                    ) : (
                        <h3>
                            References tagged:
                            <span className="ml-2 refTag">{store.selectedTag.get_full_name()}</span>
                        </h3>
                    )}
                </div>
                <div className="col-md-3">
                    {selectedReferencesLoading ? <Loading /> : null}
                    {selectedReferences && selectedReferences.length > 0 ? (
                        <>
                            <YearHistogram references={selectedReferences} />
                            <div id="reference-list" className="list-group">
                                {selectedReferences.map(referenceListItem)}
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
                        {selectedReferences ? (
                            <ReferenceTable references={selectedReferences} showActions={canEdit} />
                        ) : null}
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
