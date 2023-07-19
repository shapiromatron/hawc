import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {OVERRIDE_SCORE_LABEL_MAPPING} from "riskofbias/constants";
import SelectInput from "shared/components/SelectInput";

class OverrideObjectTypeSelector extends Component {
    render() {
        let {choices, value, onChange} = this.props;
        return (
            <SelectInput
                label="Override type"
                choices={choices}
                multiple={false}
                value={value}
                handleSelect={onChange}
            />
        );
    }
}

OverrideObjectTypeSelector.propTypes = {
    choices: PropTypes.arrayOf(PropTypes.object).isRequired,
    value: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};

class OverrideObjectsSelector extends Component {
    render() {
        let {choices, value, onChange} = this.props;
        return (
            <SelectInput
                label="Select objects"
                choices={choices}
                multiple={true}
                value={value}
                handleSelect={onChange}
            />
        );
    }
}

OverrideObjectsSelector.propTypes = {
    choices: PropTypes.arrayOf(PropTypes.object).isRequired,
    value: PropTypes.array.isRequired,
    onChange: PropTypes.func.isRequired,
};

@inject("store")
@observer
class ScoreOverrideForm extends Component {
    render() {
        const {store, score} = this.props,
            {overrideDataTypeValue} = score,
            overrideDataTypeChoices = _.chain(store.overrideOptions)
                .keys()
                .map(key => {
                    return {id: key, label: OVERRIDE_SCORE_LABEL_MAPPING[key]};
                })
                .value(),
            overrideObjectChoices =
                overrideDataTypeValue !== null
                    ? _.chain(store.overrideOptions[overrideDataTypeValue])
                          .map(option => {
                              return {id: option[0], label: option[1]};
                          })
                          .value()
                    : null,
            overrideOptionValues = score.overridden_objects.map(object => object.object_id);

        if (overrideDataTypeValue === null) {
            return <p>No extracted data is available for this study to use for overrides.</p>;
        }

        return (
            <div className="row">
                <div className="col-lg-4">
                    <OverrideObjectTypeSelector
                        choices={overrideDataTypeChoices}
                        value={overrideDataTypeValue}
                        onChange={value => {
                            store.updateScoreState(score, "overridden_objects", []);
                            store.updateScoreState(score, "overrideDataTypeValue", value);
                        }}
                    />
                </div>
                <div className="col-lg-8">
                    <OverrideObjectsSelector
                        choices={overrideObjectChoices}
                        value={overrideOptionValues}
                        onChange={values => {
                            let selected = _.map(values, value => {
                                return {
                                    content_type_name: overrideDataTypeValue,
                                    object_id: parseInt(value),
                                };
                            });
                            store.updateScoreState(score, "overridden_objects", selected);
                        }}
                    />
                </div>
            </div>
        );
    }
}

ScoreOverrideForm.propTypes = {
    store: PropTypes.object,
    score: PropTypes.object.isRequired,
};

export default ScoreOverrideForm;
