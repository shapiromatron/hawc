import PropTypes from "prop-types";
import React, {Component} from "react";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";

import DatasetPreview from "../summary/heatmap/DatasetPreview";

@inject("store")
@observer
class DataTab extends Component {
    render() {
        const {dataset} = this.props.store;
        return <DatasetPreview dataset={toJS(dataset)} />;
    }
}
DataTab.propTypes = {
    store: PropTypes.object,
};
export default DataTab;
