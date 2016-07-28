import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchObjectsIfNeeded } from 'textCleanup/actions/Items';
import ItemList from 'textCleanup/components/Items/ItemList';
import Loading from 'shared/components/Loading';


class Items extends Component {

    componentWillMount() {
        this.props.dispatch(fetchObjectsIfNeeded());
    }

    render() {
        if (_.isEmpty(this.props.items)) return <Loading />;
        return <ItemList {...this.props}/>;
    }
}

function mapStateToProps(state) {
    return {
        items: state.items.list,
    };
}
export default connect(mapStateToProps)(Items);
