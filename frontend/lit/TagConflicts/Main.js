import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import TagTree from "../components/TagTree";

@inject("store")
@observer
class TagConflictsMain extends Component {
    constructor(props) {
        super(props);
        this.savedPopup = React.createRef();
    }
    render() {
        const {store} = this.props;
        return (
            <TagTree
                tagtree={toJS(store.tagtree)}
                handleTagClick={tag => {
                    tag;
                }}
            />
        );
    }
}

TagConflictsMain.propTypes = {
    store: PropTypes.object,
};

export default TagConflictsMain;
