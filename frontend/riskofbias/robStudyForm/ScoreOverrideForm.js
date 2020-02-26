import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";
import SelectInput from "shared/components/SelectInput";
import {OVERRIDE_SCORE_LABEL_MAPPING} from "riskofbias/constants";

@inject("store")
@observer
class ScoreOverrideForm extends Component {
    render() {
        const {store, score} = this.props;

        if (score.is_default) {
            return null;
        }

        const dataTypeOptions = _.chain(store.overrideOptions)
            .keys()
            .filter(key => store.overrideOptions[key].length > 0)
            .map(key => {
                return {id: key, value: OVERRIDE_SCORE_LABEL_MAPPING[key]};
            })
            .value();

        if (dataTypeOptions.length == 0) {
            return <p>No extracted data is available for this study for overrides.</p>;
        }

        const overrideTypeValue = dataTypeOptions[0].id,
            overrideOptions = _.chain(store.overrideOptions[overrideTypeValue])
                .map(option => {
                    return {id: option[0], value: option[1]};
                })
                .value();

        return (
            <div className="row-fluid form-inline">
                <SelectInput
                    className="span6"
                    id={`${score.id}-overrideType`}
                    label="Override type"
                    choices={dataTypeOptions}
                    multiple={false}
                    value={dataTypeOptions[0].id}
                    handleSelect={value => {
                        // score.score = parseInt(value);
                    }}
                />
                <SelectInput
                    className="span6"
                    id={`${score.id}-overrides`}
                    label="Overrides"
                    choices={overrideOptions}
                    multiple={true}
                    value={[]}
                    handleSelect={value => {
                        // score.score = parseInt(value);
                    }}
                />
            </div>
        );
    }
}

ScoreOverrideForm.propTypes = {
    store: PropTypes.object,
    score: PropTypes.object.isRequired,
};

export default ScoreOverrideForm;
