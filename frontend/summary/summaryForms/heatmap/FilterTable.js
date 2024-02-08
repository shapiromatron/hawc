import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import {
    DATA_FILTER_LOGIC_CUSTOM,
    DATA_FILTER_LOGIC_OPTIONS,
    DATA_FILTER_OPTIONS,
    filterLogicHelpText,
    filterQueryHelpText,
    readableCustomQueryFilters,
} from "../../summary/filters";

const dataKey = "filters",
    FilterRow = observer(props => {
        const {store, index, filter} = props;
        return (
            <tr key={index}>
                <td>{index + 1}</td>
                <td>
                    <SelectInput
                        choices={store.getColumnsOptionsWithNull}
                        handleSelect={value =>
                            store.changeSettings(`filters.${index}.column`, value)
                        }
                        value={filter.column}
                    />
                </td>
                <td>
                    <SelectInput
                        choices={DATA_FILTER_OPTIONS}
                        handleSelect={value => store.changeSettings(`filters.${index}.type`, value)}
                        value={filter.type}
                    />
                </td>
                <td>
                    <TextInput
                        name={`filters.${index}.value`}
                        value={filter.value}
                        onChange={e => store.changeSettings(e.target.name, e.target.value)}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => store.moveArrayElementUp(dataKey, index)}
                    onMoveDown={() => store.moveArrayElementDown(dataKey, index)}
                    onDelete={() => store.deleteArrayElement(dataKey, index)}
                />
            </tr>
        );
    });

FilterRow.propTypes = {
    store: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
    filter: PropTypes.object.isRequired,
};

@inject("store")
@observer
class FilterTable extends Component {
    render() {
        const store = this.props.store.subclass,
            {filters, filtersLogic, filtersQuery} = store.settings,
            filtersQueryReadable = readableCustomQueryFilters(filters, filtersQuery);
        return (
            <>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="10%" />
                        <col width="35%" />
                        <col width="15%" />
                        <col width="25%" />
                        <col width="10%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Row #</th>
                            <th>Data column</th>
                            <th>Filter type</th>
                            <th>Value</th>
                            <ActionsTh onClickNew={store.createNewFilter} />
                        </tr>
                    </thead>
                    <tbody>
                        {filters.map((filter, index) => (
                            <FilterRow key={index} store={store} index={index} filter={filter} />
                        ))}
                    </tbody>
                </table>
                <div className="col-md-12">
                    <RadioInput
                        label="Filter logic:"
                        name="filtersLogic"
                        helpText={filterLogicHelpText}
                        onChange={value => store.changeSettings("filtersLogic", value)}
                        value={filtersLogic}
                        horizontal={true}
                        choices={DATA_FILTER_LOGIC_OPTIONS}
                    />
                    {filtersLogic === DATA_FILTER_LOGIC_CUSTOM ? (
                        <>
                            <TextInput
                                value={filtersQuery}
                                helpText={filterQueryHelpText}
                                onChange={e => store.changeSettings("filtersQuery", e.target.value)}
                            />
                            <pre>
                                <code>{filtersQueryReadable}</code>
                            </pre>
                        </>
                    ) : null}
                </div>
            </>
        );
    }
}
FilterTable.propTypes = {
    store: PropTypes.object,
};

export default FilterTable;
