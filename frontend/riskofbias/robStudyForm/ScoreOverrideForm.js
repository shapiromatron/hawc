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
        const {store, score} = this.props,
            hasOverrideObjects = score.overridden_objects.length > 0;

        if (score.is_default) {
            return null;
        }

        const dataTypeOptions = _.chain(store.overrideOptions)
            .keys()
            .filter(key => store.overrideOptions[key].length > 0)
            .map(key => {
                return {id: key, label: OVERRIDE_SCORE_LABEL_MAPPING[key]};
            })
            .value();

        if (dataTypeOptions.length == 0) {
            return <p>No extracted data is available for this study for overrides.</p>;
        }

        const overrideTypeValue = hasOverrideObjects
                ? score.overridden_objects[0].content_type_name
                : dataTypeOptions[0].id,
            overrideOptions = _.chain(store.overrideOptions[overrideTypeValue])
                .map(option => {
                    return {id: option[0], label: option[1]};
                })
                .value(),
            overrideOptionValues = score.overridden_objects.map(object => object.object_id);

        return (
            <div className="row-fluid form-inline">
                <SelectInput
                    className="span6"
                    id={`${score.id}-overrideType`}
                    label="Override type"
                    choices={dataTypeOptions}
                    multiple={false}
                    value={overrideTypeValue}
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
                    value={overrideOptionValues}
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
