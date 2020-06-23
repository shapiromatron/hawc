import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class CustomizeTab extends Component {
    render() {
        const {store} = this.props;
        return (
            <div>
                <p className="help-block">
                    Use the dashboard-selection in the top-right corner to select predefined data
                    visualizations for this dataset. You can further customize the visualization by
                    modifying the settings below. If you are part of the project-team, you can
                    create a fully customized heatmap visual using data internal or external to HAWC
                    by creating a custom visual.
                </p>
                <div className="row-fluid">
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.axisOptions}
                            handleSelect={value => store.changeAxis("selectedXAxis", value)}
                            value={store.selectedXAxis.id}
                            label="Selected X axis"
                            multiple={false}
                        />
                    </div>
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.axisOptions}
                            handleSelect={value => store.changeAxis("selectedYAxis", value)}
                            value={store.selectedYAxis.id}
                            label="Selected Y axis"
                            multiple={false}
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.filterOptions}
                            value={store.selectedFilters.map(d => d.id)}
                            handleSelect={values => store.changeSelectedFilters(values)}
                            multiple={true}
                            label="Selected filters"
                        />
                    </div>
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.tableOptions}
                            value={store.selectedTableFields.map(d => d.id)}
                            handleSelect={values => store.changeSelectedTableFields(values)}
                            multiple={true}
                            label="Selected table fields"
                        />
                    </div>
                </div>
            </div>
        );
    }
}
CustomizeTab.propTypes = {
    store: PropTypes.object,
};
export default CustomizeTab;
