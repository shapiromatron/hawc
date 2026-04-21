import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class Widgets extends React.Component {
    render() {
        const {store} = this.props,
            {settings} = this.props.store;
        return (
            <div className="row">
                <div className="col-md-4">
                    <SelectInput
                        choices={store.doseOptions}
                        value={settings.doses}
                        handleSelect={values =>
                            store.changeSettingsSelection(
                                "doses",
                                values.map(d => parseInt(d))
                            )
                        }
                        multiple={true}
                        selectSize={10}
                        label="Dose(s)"
                    />
                </div>
                <div className="col-md-4">
                    <SelectInput
                        choices={store.systemOptions}
                        value={settings.systems}
                        handleSelect={values => store.changeSettingsSelection("systems", values)}
                        multiple={true}
                        selectSize={10}
                        label="System(s)"
                    />
                </div>
                <div className="col-md-4">
                    <SelectInput
                        choices={store.criticalValueOptions}
                        value={settings.criticalValues}
                        handleSelect={values =>
                            store.changeSettingsSelection("criticalValues", values)
                        }
                        multiple={true}
                        selectSize={5}
                        label="Critical value(s)"
                    />
                    <CheckboxInput
                        label="Approximate x-values"
                        checked={store.settings.approximateXValues}
                        onChange={e =>
                            store.changeSettingsSelection(e.target.name, e.target.checked)
                        }
                        name="approximateXValues"
                        helpText="Add jitter to x-axis to reduce peaks; values on x axis are approximate"
                    />
                </div>
            </div>
        );
    }
}
Widgets.propTypes = {
    store: PropTypes.object,
};

export default Widgets;
