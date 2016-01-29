import React, { Component, PropTypes } from 'react';

export default class Root extends Component {

    render() {
        return (
            <h1>Rob filter root</h1>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};
