import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import DomainReadOnlyTable from "./DomainReadOnlyTable";
import DomainTable from "./DomainTable";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
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
            <Component
                key={domain.id}
                domain={domain}
                domainIndex={domainIndex}
                domainCount={store.domains.length}
            />
        ));
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
