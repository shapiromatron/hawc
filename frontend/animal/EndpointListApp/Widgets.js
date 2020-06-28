import PropTypes from "prop-types";
import React from "react";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class Widgets extends React.Component {
    render() {
        const {store} = this.props,
            {settings} = this.props.store;
        return (
            <div className="row-fluid">
                <div className="span4">
                    <SelectInput
                        className="span12"
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
                <div className="span4">
                    <SelectInput
                        className="span12"
                        choices={store.systemOptions}
                        value={settings.systems}
                        handleSelect={values => store.changeSettingsSelection("systems", values)}
                        multiple={true}
                        selectSize={10}
                        label="System(s)"
                    />
                </div>
                <div className="span4">
                    <SelectInput
                        className="span12"
                        choices={store.criticalValueOptions}
                        value={settings.criticalValues}
                        handleSelect={values =>
                            store.changeSettingsSelection("criticalValues", values)
                        }
                        multiple={true}
                        selectSize={10}
                        label="Critical value(s)"
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
