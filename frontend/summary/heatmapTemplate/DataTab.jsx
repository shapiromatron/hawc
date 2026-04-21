import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import DatasetPreview from "../summary/heatmap/DatasetPreview";

@inject("store")
@observer
class DataTab extends Component {
    render() {
        const {config, dataset, settings} = this.props.store;
        return (
            <DatasetPreview
                dataset={toJS(dataset)}
                url={settings.data_url}
                clearCacheUrl={config.clear_cache_url}
            />
        );
    }
}
DataTab.propTypes = {
    store: PropTypes.object,
};
export default DataTab;
