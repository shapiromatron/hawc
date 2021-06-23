import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class ScoreSelect extends Component {
    render() {
        const {scoreOptions, changeSelectedScores, selectedScores} = this.props.store;
        return (
            <SelectInput
                id="score_filter"
                name="score_filter"
                label="Rating filter (optional)"
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
