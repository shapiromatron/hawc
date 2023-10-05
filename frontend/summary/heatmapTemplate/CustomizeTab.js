import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

@inject("store")
@observer
class CustomizeTab extends Component {
    render() {
        const {store} = this.props,
            {create_visual_url} = store.config;
        return (
            <div className="container-fluid">
                <p className="form-text text-muted">
                    Use the dashboard-selection in the top-right corner to select predefined data
                    visualizations for this dataset. You can further customize the visualization by
                    modifying the settings below. If you are part of the project-team, you can&nbsp;
                    {create_visual_url ? <a href={create_visual_url}>create</a> : "create"}&nbsp;a
                    fully customized heatmap visual using data internal or external to HAWC.
                </p>
                <div className="row">
                    <div className="col-md-6">
                        <SelectInput
                            choices={store.axisOptions}
                            handleSelect={value => store.changeAxis("selectedYAxis", value)}
                            value={store.selectedYAxis.id}
                            label="Y axis"
                            multiple={false}
                        />
                    </div>
                    <div className="col-md-6">
                        <SelectInput
                            choices={store.axisOptions}
                            handleSelect={value => store.changeAxis("selectedXAxis", value)}
                            value={store.selectedXAxis.id}
                            label="X axis"
                            multiple={false}
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6">
                        <SelectInput
                            choices={store.filterOptions}
                            value={store.selectedFilters.map(d => d.id)}
                            handleSelect={values => store.changeSelectedFilters(values)}
                            multiple={true}
                            selectSize={10}
                            label="Data filters"
                        />
                    </div>
                    <div className="col-md-6">
                        <SelectInput
                            choices={store.tableOptions}
                            value={store.selectedTableFields.map(d => d.id)}
                            handleSelect={values => store.changeSelectedTableFields(values)}
                            multiple={true}
                            selectSize={10}
                            label="Table fields"
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4">
                        <CheckboxInput
                            label="Show null field values"
                            name="show_null"
                            onChange={e => store.changeShowNull(e.target.checked)}
                            checked={store.showNull}
                            helpText={"Display data with <null> values in selected axes."}
                        />
                    </div>
                    <div className="col-md-4">
                        <CheckboxInput
                            label="Show value counts"
                            name="show_counts"
                            onChange={e => store.changeShowCounts(e.target.checked)}
                            checked={store.showCounts}
                            helpText={"Show count information in heatmap and filters."}
                        />
                    </div>
                    <div className="col-md-4">
                        <TextInput
                            label="Color"
                            name="upperColor"
                            type="color"
                            value={store.upperColor}
                            onChange={e => store.changeUpperColor(e.target.value)}
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
