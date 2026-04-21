import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

import {ReferenceStorageKey, SortBy} from "../constants";

@observer
class ReferenceSortSelector extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value: window.localStorage.getItem(ReferenceStorageKey) || SortBy.YEAR_DESC[0],
        };
    }
    render() {
        const choices = _.map(SortBy, (v, _k) => {
            return {id: v[0], label: v[1]};
        });
        return (
            <div className="dropdown float-right">
                <button
                    className="btn btn-sm btn-light"
                    title="Reference ordering"
                    type="button"
                    data-toggle="dropdown"
                    aria-haspopup="true"
                    aria-expanded="false">
                    <i className="fa fa-fw fa-sort"></i>
                </button>
                <form className="dropdown-menu dropdown-menu-right p-3">
                    <div className="form-group">
                        <SelectInput
                            name="sortReferencesBy"
                            label="Ordering"
                            value={this.state.value}
                            choices={choices}
                            handleSelect={value => {
                                window.localStorage.setItem(ReferenceStorageKey, value);
                                this.setState({value});
                                this.props.onChange(value);
                            }}
                        />
                    </div>
                </form>
            </div>
        );
    }
}
ReferenceSortSelector.propTypes = {
    onChange: PropTypes.func.isRequired,
};

export default ReferenceSortSelector;
