import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";
import _ from "lodash";

import {fetchObjects} from "textCleanup/actions/Items";
import ItemList from "textCleanup/components/Items/ItemList";
import Loading from "shared/components/Loading";

class Items extends Component {
    componentDidMount() {
        this.props.dispatch(fetchObjects({routerParams: this.props.match.params}));
    }

    render() {
        const {items, match} = this.props;
        if (_.isEmpty(items)) return <Loading />;
        return <ItemList items={items} params={match.params} />;
    }
}

function mapStateToProps(state) {
    return {
        items: state.items.list,
    };
}

Items.propTypes = {
    dispatch: PropTypes.func,
    match: PropTypes.shape({
        params: PropTypes.object,
    }),
    items: PropTypes.array,
};

export default connect(mapStateToProps)(Items);
