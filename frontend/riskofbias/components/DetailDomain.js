import React from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

const DetailDomain = props => {
    const {object} = props;
    return (
        <ul className="mb-0">
            <li>Name: {object.name}</li>
            <li>
                Overall confidence:&nbsp;
                {h.booleanCheckbox(object.is_overall_confidence)}
            </li>
            <li>
                <b>Description:&nbsp;</b>
                <span dangerouslySetInnerHTML={{__html: object.description}}></span>
            </li>
        </ul>
    );
};

DetailDomain.propTypes = {
    object: PropTypes.object.isRequired,
};
export default DetailDomain;
