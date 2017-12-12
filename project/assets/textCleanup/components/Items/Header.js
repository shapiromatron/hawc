import React, { Component } from 'react';

import h from 'textCleanup/utils/helpers';

class Header extends Component {
    render() {
        let { params } = this.props;
        return (
            <h2 className="item_list_title">
                {`${h.caseToWords(params.field)} data cleanup`}
            </h2>
        );
    }
}

export default Header;
