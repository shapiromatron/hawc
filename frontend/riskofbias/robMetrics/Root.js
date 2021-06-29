import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import DomainTable from "./DomainTable";
import DomainReadOnlyTable from "./DomainReadOnlyTable";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.setConfig("config");
        this.props.store.fetchRoBData();
    }

    render() {
        let {store} = this.props;

        if (!store.dataLoaded) {
            return <Loading />;
        }

        let {isEditing} = store,
            Component = isEditing ? DomainTable : DomainReadOnlyTable;

        return store.domains.map((domain, domainIndex) => (
            <Component key={domain.id} domain={domain} domainIndex={domainIndex} />
        ));
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
