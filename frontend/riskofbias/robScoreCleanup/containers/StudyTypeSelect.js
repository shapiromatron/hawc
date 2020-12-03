import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import LabelInput from "shared/components/LabelInput";

import h from "shared/utils/helpers";

@inject("store")
@observer
class StudyTypeSelect extends Component {
    render() {
        const choices = this.props.store.studyTypeOptions,
            selected = this.props.store.selectedStudyTypes,
            handleChange = e => {
                const values = _.chain(e.target.options)
                    .filter(o => o.selected)
                    .map(o => o.value)
                    .value();
                this.props.store.changeSelectedStudyType(values);
            };

        return (
            <div className="form-group">
                <LabelInput for="studyType_filter" label="Study Type filter (optional)" />
                <select
                    multiple
                    name="studyType_filter"
                    id="studyType_filter"
                    className="form-control"
                    onChange={handleChange}
                    style={{height: "120px"}}>
                    value={selected}
                    {_.map(choices, (type, i) => {
                        return (
                            <option key={i} value={type}>
                                {h.caseToWords(type)}
                            </option>
                        );
                    })}
                </select>
            </div>
        );
    }
}
StudyTypeSelect.propTypes = {
    store: PropTypes.object,
};

export default StudyTypeSelect;
