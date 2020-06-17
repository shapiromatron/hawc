import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class SettingsTab extends Component {
    render() {
        const {store} = this.props,
            handleFilterChange = () => {
                const values = _.chain(event.target.options)
                    .filter(o => o.selected)
                    .map(o => o.value)
                    .value();
                store.changeSelectedFilters(values);
            };
        return (
            <div>
                <SelectInput
                    choices={store.axisOptions}
                    handleSelect={value => store.changeAxis("selectedXAxis", value)}
                    value={store.selectedXAxis.id}
                    label="Selected X axis"
                    multiple={false}
                />
                <SelectInput
                    choices={store.axisOptions}
                    handleSelect={value => store.changeAxis("selectedYAxis", value)}
                    value={store.selectedYAxis.id}
                    label="Selected Y axis"
                    multiple={false}
                />
                <SelectInput
                    choices={store.filterOptions}
                    value={store.selectedFilters.map(d => d.id)}
                    handleSelect={handleFilterChange}
                    multiple={true}
                    label="Selected filters"
                />
            </div>
        );
    }
}
SettingsTab.propTypes = {
    store: PropTypes.object,
};
export default SettingsTab;
