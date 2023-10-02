import _ from "lodash";
import h from "shared/utils/helpers";

class EndpointCriticalDose {
    constructor(endpoint, span, type) {
        // custom field to observe dose changes and respond based on selected dose
        endpoint.addObserver(this);
        this.endpoint = endpoint;
        this.span = span;
        this.type = type;
        this.critical_effect_idx = endpoint.data[type];
        this.update();
    }

    update() {
        const dose_group_id = this.critical_effect_idx,
            dose_units_id = this.endpoint.doseUnits.activeUnit.id,
            group = _.find(this.endpoint.data.animal_group.dosing_regime.doses, el => {
                return el.dose_group_id === dose_group_id && el.dose_units.id === dose_units_id;
            }),
            dose = group ? h.ff(group.dose) : "",
            units = group ? group.dose_units.name : "",
            text = `${dose} ${units}`;
        this.span.text(text);
    }
}

export default EndpointCriticalDose;
