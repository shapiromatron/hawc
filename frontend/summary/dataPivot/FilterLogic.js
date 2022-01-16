import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";

import RadioInput from "shared/components/RadioInput";
import TextInput from "shared/components/TextInput";
import {FilterLogicChoices} from "./shared";
import {filterLogicHelpText, filterQueryHelpText} from "../summary/filters";

const choices = [
    {id: FilterLogicChoices.and, label: "AND"},
    {id: FilterLogicChoices.or, label: "OR"},
    {id: FilterLogicChoices.custom, label: "CUSTOM"},
];

@observer
class FilterLogic extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.plotSettingsStore;
        return (
            <>
                <h4>Filter logic</h4>
                <RadioInput
                    name="filter_logic"
                    onChange={value => store.updateFilterLogic(value)}
                    choices={choices}
                    required={false}
                    horizontal={true}
                    value={store.settings.filter_logic}
                    helpText={filterLogicHelpText}
                />
                {store.settings.filter_logic === FilterLogicChoices.custom ? (
                    <TextInput
                        name="filter_query"
                        onChange={e => store.updateFilterQuery(e.target.value)}
                        required={false}
                        value={store.settings.filter_query}
                        helpText={filterQueryHelpText}
                    />
                ) : null}
                <hr />
            </>
        );
    }
}
FilterLogic.propTypes = {
    dp: PropTypes.object,
};

export default (tab, dp) => {
    const div = document.createElement("div");
    ReactDOM.render(<FilterLogic dp={dp} />, div);
    tab.append(div);
};
