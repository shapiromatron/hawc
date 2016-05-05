import React, { Component } from 'react';

import h from 'textCleanup/utils/helpers';


class Header extends Component {

    render() {
        let { params } = this.props;
        return (
            <h2 className='endpoint_list_title'>
                {`${h.caseToWords(params.field)} endpoint cleanup`}
            </h2>
        );
    }
}

export default Header;
