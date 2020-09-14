import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import ReferenceTable from "../components/ReferenceTable";
import TagTree from "../components/TagTree";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class ReferenceTreeMain extends Component {
    render() {
        const {store} = this.props,
            actions = store.getActionLinks,
            {selectedReferences, selectedReferencesLoading} = store,
            {canEdit} = store.config;

        return (
            <div className="row-fluid">
                <div className="span3">
                    <h3>Taglist</h3>
                    <TagTree
                        tagtree={toJS(store.tagtree)}
                        handleTagClick={tag => store.handleTagClick(tag)}
                        showReferenceCount={true}
                    />
                    <br />
                    <p
                        className="nestedTag"
                        id="untaggedReferences"
                        onClick={() => store.handleUntaggedReferenceClick(null)}>
                        Untagged References: ({store.config.untaggedReferenceCount})
                    </p>
                </div>
                <div className="span9">
                    {actions.length > 0 ? (
                        <div className="btn-group pull-right">
                            <a className="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Actions <span className="caret"></span>
                            </a>
                            <ul className="dropdown-menu">
                                {actions.map((action, index) => (
                                    <li key={index}>
                                        <a href={action[0]}>{action[1]}</a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ) : null}

                    <div id="references_detail_div">
                        {store.untaggedReferencesSelected === true ? (
                            <h3>Untagged references</h3>
                        ) : store.selectedTag === null ? (
                            <h3>Available references</h3>
                        ) : (
                            <h3>
                                References tagged:&nbsp;
                                <span className="refTag">{store.selectedTag.get_full_name()}</span>
                            </h3>
                        )}
                        {selectedReferencesLoading ? <Loading /> : null}
                        {store.selectedTag === null &&
                        store.untaggedReferencesSelected === false ? (
                            <p className="help-block">Click on a tag to view tagged references.</p>
                        ) : null}
                        {selectedReferences ? (
                            <ReferenceTable references={selectedReferences} showActions={canEdit} />
                        ) : null}
                    </div>
                </div>
            </div>
        );
    }
}

ReferenceTreeMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceTreeMain;
