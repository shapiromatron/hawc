import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import h from "shared/utils/helpers";

import $ from "$";

class Store {
    constructor(config, formField) {
        this.options = config.preferred_units;
        this.selected = config.preferred_units_initial
            ? (this.selected = config.preferred_units_initial.map(selected => {
                  return _.find(config.preferred_units, unit => selected == unit.id);
              }))
            : [];
        this.formField = formField;
        autorun(() => {
            formField.value = this.selected.map(d => d.id.toString()).join(",");
        });
    }
    @observable selected = [];
    @action.bound add(ids) {
        const additions = [];
        ids.map(id => {
            const option = _.find(this.options, d => d.id == id);
            additions.push(option);
        });
        this.selected.push(...additions);
    }
    @action.bound remove(ids) {
        const removals = new Set(ids);
        this.selected = this.selected.filter(d => !removals.has(d.id));
    }
    @action.bound moveUp(indexes) {
        indexes.forEach(index => h.moveArrayElementUp(this.selected, index));
    }
    @action.bound moveDown(indexes) {
        _.reverse(indexes).forEach(index => h.moveArrayElementDown(this.selected, index));
    }
    @computed get available() {
        const selected = new Set(this.selected.map(d => d.id));
        return this.options.filter(opt => !selected.has(opt.id));
    }
}

@observer
class PreferredUnits extends Component {
    constructor(props) {
        super(props);
        this.available = React.createRef();
        this.selected = React.createRef();
    }
    render() {
        const {store} = this.props;
        return (
            <div className="row">
                <div className="col-md-4">
                    <label className="col-form-label">Available doses</label>
                    <select ref={this.available} className="form-control" multiple size="10">
                        {store.available.map(d => (
                            <option key={d.id} value={d.id}>
                                {d.label}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="col-md-2 text-center">
                    <br />
                    <br />
                    <br />
                    <br />
                    <button
                        className="btn btn-block btn-secondary"
                        type="button"
                        title="Add selected units to preferred-list"
                        onClick={e => {
                            const selected = h.selectedOptions(this.available.current);
                            store.add(selected.values);
                        }}>
                        Add
                        <i className="fa fa-chevron-right"></i>
                    </button>
                    <button
                        className="btn btn-block btn-secondary"
                        type="button"
                        title="Remove selected units from preferred-list"
                        onClick={e => {
                            const selected = h.selectedOptions(this.selected.current);
                            store.remove(selected.values);
                        }}>
                        <i className="fa fa-chevron-left"></i>Remove
                    </button>
                </div>
                <div className="col-md-4">
                    <label className="col-form-label">Selected doses</label>
                    <select ref={this.selected} className="form-control" multiple size="10">
                        {store.selected.map(d => (
                            <option key={d.id} value={d.id}>
                                {d.label}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="col-md-2">
                    <br />
                    <br />
                    <br />
                    <br />
                    <button
                        className="btn btn-block btn-secondary"
                        type="button"
                        title="Move selected units higher in preference"
                        onClick={e => {
                            const selected = h.selectedOptions(this.selected.current);
                            store.moveUp(selected.indexes);
                        }}>
                        <i className="fa fa-chevron-up"></i>
                    </button>
                    <button
                        className="btn btn-block btn-secondary"
                        type="button"
                        title="Move selected units lower in preference"
                        onClick={e => {
                            const selected = h.selectedOptions(this.selected.current);
                            store.moveDown(selected.indexes);
                        }}>
                        <i className="fa fa-chevron-down"></i>
                    </button>
                </div>
            </div>
        );
    }
}
PreferredUnits.propTypes = {
    store: PropTypes.object.isRequired,
};

export default (formField, config) => {
    const container = $("<div>").insertBefore(formField),
        store = new Store(config, formField);
    ReactDOM.render(<PreferredUnits store={store} />, container[0]);
    $(formField).hide();
};
