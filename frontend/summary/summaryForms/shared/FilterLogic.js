import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import RadioInput from "shared/components/RadioInput";
import TextInput from "shared/components/TextInput";

import {
    DATA_FILTER_LOGIC_CUSTOM,
    DATA_FILTER_LOGIC_OPTIONS,
    filterLogicHelpText,
    filterQueryHelpText,
} from "../../summary/filters";

@observer
class FilterLogic extends Component {
    render() {
        const {filtersLogic, filtersQuery, filtersQueryReadable, onLogicChange, onQueryChange} =
            this.props;
        return (
            <div className="col-md-12">
                <RadioInput
                    label="Filter logic:"
                    name="filtersLogic"
                    helpText={filterLogicHelpText}
                    onChange={onLogicChange}
                    value={filtersLogic}
                    horizontal={true}
                    choices={DATA_FILTER_LOGIC_OPTIONS}
                />
                {filtersLogic === DATA_FILTER_LOGIC_CUSTOM ? (
                    <>
                        <TextInput
                            name="filtersLogicQuery"
                            value={filtersQuery}
                            helpText={filterQueryHelpText}
                            onChange={onQueryChange}
                        />
                        <pre>
                            <code>{filtersQueryReadable}</code>
                        </pre>
                    </>
                ) : null}
            </div>
        );
    }
}
FilterLogic.propTypes = {
    filtersLogic: PropTypes.string,
    filtersQuery: PropTypes.string,
    filtersQueryReadable: PropTypes.string,
    onLogicChange: PropTypes.func,
    onQueryChange: PropTypes.func,
};

export default FilterLogic;
