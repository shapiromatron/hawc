import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";
import CheckboxInput from "shared/components/CheckboxInput";

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
                            label="X axis"
                            multiple={false}
                        />
                    </div>
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.axisOptions}
                            handleSelect={value => store.changeAxis("selectedYAxis", value)}
                            value={store.selectedYAxis.id}
                            label="Y axis"
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
                            selectSize={10}
                            label="Data filters"
                        />
                    </div>
                    <div className="span6">
                        <SelectInput
                            className="span12"
                            choices={store.tableOptions}
                            value={store.selectedTableFields.map(d => d.id)}
                            handleSelect={values => store.changeSelectedTableFields(values)}
                            multiple={true}
                            selectSize={10}
                            label="Table fields"
                        />
                    </div>
                    <div className="row-fluid">
                        <div className="span3">
                            <CheckboxInput
                                label="Show null field values"
                                name="show_null"
                                onChange={e => store.changeShowNull(e.target.checked)}
                                checked={store.showNull}
                                helpText={"Display data with <null> values in selected axes."}
                            />
                        </div>
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
