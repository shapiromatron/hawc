import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "textCleanup/utils/helpers";

class Header extends Component {
    render() {
        let {params} = this.props;
        return <h2 className="item_list_title">{`${h.caseToWords(params.field)} data cleanup`}</h2>;
    }
}

Header.propTypes = {
    params: PropTypes.shape({
        field: PropTypes.object,
    }),
};

export default Header;
