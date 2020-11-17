import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class ScoreSelect extends Component {
    render() {
        const choices = this.props.store.scoreOptions,
            selected = this.props.store.selectedScores.map(e => e.toString()),
            handleChange = e => {
                const values = _.chain(e.target.options)
                    .filter(o => o.selected)
                    .map(o => parseInt(o.value))
                    .value();
                this.props.store.changeSelectedScores(values);
            };

        return (
            <div>
                <label className="col-form-label">Rating filter (optional):</label>
                <select
                    multiple={true}
                    name="score_filter"
                    id="score_filter"
                    onChange={handleChange}
                    style={{height: "120px"}}>
                    value={selected}
                    {_.map(choices, score => {
                        return (
                            <option key={score.id} value={score.id}>
                                {score.value}
                            </option>
                        );
                    })}
                </select>
            </div>
        );
    }
}
ScoreSelect.propTypes = {
    store: PropTypes.object,
};

export default ScoreSelect;
