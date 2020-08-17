import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class ReferenceTreeBrowse extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        const {store} = this.props,
            actions = store.getActionLinks;

        return (
            <div className="row-fluid">
                <div className="span3">
                    <h3>Taglist</h3>
                    <div id="taglist"></div>
                    <p
                        className="nestedTag"
                        id="untaggedReferences"
                        onClick={() => store.changeSelectedTag(123)}>
                        Untagged References: (123)
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
                        <h3>Available References</h3>
                        {store.selectedTag === null ? (
                            <p className="help-block">Click on a tag to view tagged references.</p>
                        ) : (
                            <p>TODO - add</p>
                        )}
                    </div>
                </div>
            </div>
        );
    }
}

ReferenceTreeBrowse.propTypes = {
    store: PropTypes.object,
};

export default ReferenceTreeBrowse;
