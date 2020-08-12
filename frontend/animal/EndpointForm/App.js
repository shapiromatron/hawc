import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import TermSelector from "./TermSelector";

@inject("store")
@observer
class App extends Component {
    render() {
        return (
            <div>
                <TermSelector
                    label={"System"}
                    termIdField={"system_term_id"}
                    termTextField={"system"}
                    parentRequired={false}
                />
                <TermSelector
                    label={"Organ"}
                    termIdField={"organ_term_id"}
                    termTextField={"organ"}
                    parentIdField={"system_term_id"}
                    parentRequired={true}
                />
                <TermSelector
                    label={"Effect"}
                    termIdField={"effect_term_id"}
                    termTextField={"effect"}
                    parentIdField={"organ_term_id"}
                    parentRequired={true}
                />
                <TermSelector
                    label={"Effect subtype"}
                    termIdField={"effect_subtype_term_id"}
                    termTextField={"effect_subtype"}
                    parentIdField={"effect_term_id"}
                    parentRequired={true}
                />
                <TermSelector
                    label={"Endpoint name"}
                    termIdField={"name_term_id"}
                    termTextField={"name"}
                    parentIdField={"effect_subtype_term_id"}
                    parentRequired={true}
                />
            </div>
        );
    }
}
export default App;
