import React, { Component } from 'react';
import h from '../../utils/helpers';

export default class EndpointHeader extends Component {

    render() {
        let { params } = this.props;
        return (
            <h2 className='endpoint_list_title'>
                {`${h.caseToWords(params.field)} Endpoint Cleanup`}
            </h2>
        );
    }
}
