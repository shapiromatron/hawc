import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

@observer
class StudyTypeSelect extends Component {
    render() {
        const {store} = this.props;
        if (!store.hasStudyTypes) {
            return null;
        }
        return (
            <SelectInput
                id="studyType_filter"
                name="studyType_filter"
                label="Study Type filter (optional)"
                multiple={true}
                style={{height: "120px"}}
                handleSelect={values => store.changeSelectedStudyType(values)}
                value={store.selectedStudyTypes}
                choices={store.studyTypeChoices}
            />
        );
    }
}
StudyTypeSelect.propTypes = {
    store: PropTypes.object.isRequired,
};

export default StudyTypeSelect;
