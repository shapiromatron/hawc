import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

@observer
class ScoreSelect extends Component {
    render() {
        const {scoreOptions, changeSelectedScores, selectedScores} = this.props.store;
        return (
            <SelectInput
                id="score_filter"
                name="score_filter"
                label="Judgment filter (optional)"
                multiple={true}
                style={{height: "120px"}}
                handleSelect={values => changeSelectedScores(values.map(d => parseInt(d)))}
                value={selectedScores}
                choices={scoreOptions}
            />
        );
    }
}
ScoreSelect.propTypes = {
    store: PropTypes.object.isRequired,
};

export default ScoreSelect;
