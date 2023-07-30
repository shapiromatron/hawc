import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

class FilterBase {
    constructor(field, values) {
        this.field = field;
        this.values = values;
    }
    filter(data) {
        throw Error("Not implemented");
    }
    isEmpty() {
        throw Error("Not implemented");
    }
}

class IntegerRangeFilter extends FilterBase {
    filter(data) {
        const min = this.values.min === null ? -Infinity : this.values.min,
            max = this.values.max === null ? Infinity : this.values.max;
        return data.filter(item => item[this.field] >= min && item[this.field] <= max);
    }
    isEmpty() {
        return this.values.min === null && this.values.max === null;
    }
}

class StringContainsFilter extends FilterBase {
    filter(data) {
        const values = new Set(this.values);
        return data.filter(item => values.has(item[this.field]));
    }
    isEmpty() {
        return this.values.length === 0;
    }
}

const getDataStack = (field, dataStack, activeFilters) => {
    const idx = _.findIndex(activeFilters, d => d.field === field);
    if (idx < 0) {
        return dataStack[dataStack.length - 1];
    }
    return dataStack[idx];
};

// TODO - generalize this table renderer; or use one of the existing ones we have?
// TODO - move range filters and select filters to common components

@inject("store")
@observer
class Table extends React.Component {
    render() {
        const {filteredData} = this.props.store;
        return (
            <>
                <p>{filteredData.length} rows matched.</p>
                <table className="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Short citation</th>
                            <th>Year</th>
                            <th>Effect</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_.map(filteredData, (row, i) => {
                            return (
                                <tr key={i}>
                                    <td>{row["endpoint id"]}</td>
                                    <td>{row["study citation"]}</td>
                                    <td>{row.year}</td>
                                    <td>{row.effect}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </>
        );
    }
}

@inject("store")
@observer
class RangeFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            min: null,
            max: null,
        };
    }

    render() {
        const {min, max} = this.state,
            {store, label, field} = this.props,
            change = (attr, value) => {
                const cleanedValue = value === "" ? null : parseInt(value);
                this.setState({
                    [attr]: cleanedValue,
                });
                let values = {min, max};
                values[attr] = cleanedValue;
                store.changeFilter(new IntegerRangeFilter(field, values));
            };
        let data = getDataStack(field, store.filteredDataStack, store.activeFilters).map(
                d => d[field]
            ),
            minValue = _.min(data),
            maxValue = _.max(data);

        return (
            <>
                <label>{label}</label>
                <br />
                <div className="row">
                    <div className="col-6">Min: {minValue}</div>
                    <div className="col-6">Max: {maxValue}</div>
                </div>
                <div className="row">
                    <div className="col-6">
                        <input
                            className="form-control"
                            type="number"
                            value={min === null ? "" : min}
                            onChange={d => change("min", event.target.value)}
                        />
                    </div>
                    <div className="col-6">
                        <input
                            className="form-control"
                            type="number"
                            value={max === null ? "" : max}
                            onChange={d => change("max", event.target.value)}
                        />
                    </div>
                    <div className="col-12">
                        <span>
                            Current min/max: {min ? min : "none"}/{max ? max : "none"}
                        </span>
                    </div>
                </div>
            </>
        );
    }
}

@inject("store")
@observer
class SelectMultipleFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            values: [],
        };
    }

    render() {
        const {label, field, store} = this.props,
            {values} = this.state,
            opts = _.chain(getDataStack(field, store.filteredDataStack, store.activeFilters))
                .map(d => d[field])
                .uniq()
                .value(),
            change = event => {
                const selectedOptions = event.target.selectedOptions,
                    values = Array.from(selectedOptions).map(option => option.value),
                    isEmpty = values.length === 0;
                this.setState({values});
                store.changeFilter(new StringContainsFilter(field, values));
            };
        return (
            <>
                <label>{label}</label>
                <br />
                <select multiple className="form-control" value={values} onChange={change}>
                    {opts.map(opt => {
                        return (
                            <option key={opt} value={opt}>
                                {opt}
                            </option>
                        );
                    })}
                </select>
                <p>{values.join(", ")}</p>
            </>
        );
    }
}

@inject("store")
@observer
class EndpointListApp extends React.Component {
    render() {
        const {store} = this.props;

        if (!store.filteredData) {
            return <Loading />;
        }

        return (
            <div>
                <div className="row" style={{minHeight: 200}}>
                    <div className="col-4">
                        <RangeFilter label="Publication Year" field="year" />
                    </div>
                    <div className="col-4">
                        <SelectMultipleFilter label="Short citation" field="study citation" />
                    </div>
                    <div className="col-4">
                        <SelectMultipleFilter label="Effect" field="effect" />
                    </div>
                </div>
                <Table />
            </div>
        );
    }
}
EndpointListApp.propTypes = {
    store: PropTypes.object,
};

export default EndpointListApp;
