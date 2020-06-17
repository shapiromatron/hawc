import React from "react";
import ReactDOM from "react-dom";
import {observable, action} from "mobx";
import {Provider, observer, inject} from "mobx-react";
import h from "shared/utils/helpers";
import Loading from "shared/components/Loading";
import DataTable from "shared/components/DataTable";
import PropTypes from "prop-types";

class Store {
    @observable dataset = null;
    @action.bound fetchDataset() {
        const url = "/assessment/api/dashboard/assessment-size/";
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.dataset = json))
            .catch(ex => console.error("Dataset fetch failed", ex));
    }
}

@inject("store")
@observer
class Root extends React.Component {
    componentDidMount() {
        this.props.store.fetchDataset();
    }
    render() {
        const {dataset} = this.props.store,
            renderers = {
                name: row => {
                    return <a href={`/assessment/${row.id}/`}>{row.name}</a>;
                },
            };

        if (dataset === null) {
            return <Loading />;
        }
        return <DataTable dataset={dataset} renderers={renderers} />;
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default function(el) {
    const store = new Store();

    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
