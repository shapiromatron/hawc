import React from 'react';
import { connect } from 'react-redux';

import Loading from 'shared/components/Loading';


class Tree extends React.Component {

    render() {
        console.log(this.props)
        if (!this.props.tagsLoaded){
            return <Loading />;
        }

        return <h1>Hi</h1>;
    }
}

function mapStateToProps(state) {
    return {
        tagsLoaded: state.tree.tagsLoaded,
    };
}

export default connect(mapStateToProps)(Tree);
