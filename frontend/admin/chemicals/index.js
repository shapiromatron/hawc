import React from "react";
import ReactDOM from "react-dom";
import {observer} from "mobx-react";
import Loading from "shared/components/Loading";
import DataTable from "shared/components/DataTable";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import PropTypes from "prop-types";
import store from "./store";
import {modelChoices} from "./constants";

@observer
class Root extends React.Component {
    componentDidMount() {
        this.props.store.fetchDataset();
    }
    renderInputs(store) {
        return (
            <div>
                <SelectInput
                    name="choice"
                    id="id_choice"
                    handleSelect={() => store.changeChoice(event.target.value)}
                    choices={modelChoices}
                    value={store.choice}
                    multiple={false}
                    label="Select model"
                />
                <TextInput
                    name="search"
                    onChange={() => store.changeSearch(event.target.value)}
                    value={store.search}
                    label="Search"
                />
            </div>
        );
    }
    render() {
        return (
            <div>
                {this.renderInputs(this.props.store)}
                {this.props.store.dataset === null ? (
                    <Loading />
                ) : (
                    <DataTable
                        dataset={this.props.store.matchingDataset}
                        renderers={this.props.store.matchingRenderer}
                    />
                )}
            </div>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default function(el) {
    ReactDOM.render(<Root store={store} />, el);
}
