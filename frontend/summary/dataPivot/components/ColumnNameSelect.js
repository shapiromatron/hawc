import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import SelectInput from "shared/components/SelectInput";

@observer
class ColumnNameSelect extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.columnNameStore;
        return (
            <SelectInput
                choices={[{id: "hi", label: "ho"}]}
                handleSelect={values => console.error(values)}
                fieldOnly={true}
            />
        );
    }
}
ColumnNameSelect.propTypes = {
    dp: PropTypes.object,
};

export default (el, dp) => {
    ReactDOM.render(<ColumnNameSelect dp={dp} />, el);
};
