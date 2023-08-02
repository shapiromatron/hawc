import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import SelectInput from "shared/components/SelectInput";
import {StringContainsFilter} from "shared/dashboard/filters";
import h from "shared/utils/helpers";

@observer
class SelectMultipleFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            values: [],
        };
    }
    render() {
        const {label, field, store, selectSize} = this.props,
            {values} = this.state,
            choices = _.chain(
                store.getDataStack(field, store.filteredDataStack, store.activeFilters)
            )
                .map(d => d[field])
                .sort()
                .uniq()
                .map(d => ({id: d, label: d || h.nullString}))
                .value(),
            onChange = values => {
                this.setState({values});
                store.changeFilter(new StringContainsFilter(field, values));
            };
        return (
            <SelectInput
                choices={choices}
                value={values}
                handleSelect={onChange}
                multiple={true}
                selectSize={selectSize}
                label={label}
            />
        );
    }
}
SelectMultipleFilter.propTypes = {
    label: PropTypes.string.isRequired,
    field: PropTypes.string.isRequired,
    store: PropTypes.object,
    selectSize: PropTypes.number,
};
SelectMultipleFilter.defaultProps = {
    selectSize: 10,
};

@inject("store")
@observer
class Widgets extends React.Component {
    render() {
        const {store} = this.props,
            {filterStore} = store;
        return (
            <div className="row">
                <div className="col-md-4">
                    <SelectMultipleFilter
                        label="Doses"
                        field="dose units name"
                        store={filterStore}
                    />
                </div>
                <div className="col-md-4">
                    <SelectMultipleFilter label="Systems" field="system" store={filterStore} />
                </div>
                <div className="col-md-4">
                    <SelectMultipleFilter
                        label="Critical value"
                        field="type"
                        store={filterStore}
                        selectSize={5}
                    />
                    <CheckboxInput
                        label="Approximate x-values"
                        checked={store.settings.approximateXValues}
                        onChange={e =>
                            store.changeSettingsSelection(e.target.name, e.target.checked)
                        }
                        name="approximateXValues"
                        helpText="Add jitter to x-axis to reduce peaks; values on x axis are approximate"
                    />
                </div>
            </div>
        );
    }
}
Widgets.propTypes = {
    store: PropTypes.object,
};

export default Widgets;
