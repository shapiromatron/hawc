import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import urls from '../constants/urls';
import h from '../utils/helpers';

export default class EndpointList extends Component {
    renderEndpoint(endpoint){

    }

    render() {
        const { endpoints, params } = this.props;
        return (
            <div className='endpoint_list'>
                <h2 className='endpoint_list_title'>
                    {`${h.caseToWords(params.field)} ${urls.endpoints.name}`}
                </h2>
                <table className='table table-condensed table-striped'>
                    <colgroup>
                        <col style={{width: '20%'}} />
                        <col style={{width: '20%'}} />
                        <col style={{width: '38%'}} />
                        <col style={{width: '11%'}} />
                    </colgroup>
                    <thead></thead>
                    <tbody></tbody>
                </table>
            </div>
        );
    }
}
