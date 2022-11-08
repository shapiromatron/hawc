import PropTypes from "prop-types";
import React from "react";
import h from "shared/utils/helpers";

const DetailDomain = props => {
    const {object} = props;
    return (
        <div className="row mr-1" style={{maxHeight: 300, overflowY: "auto"}}>
            <div className="col-md-4">
                <ul className="mb-0">
                    <li>
                        <b>Name:&nbsp;</b>
                        {object.name}
                    </li>
                    <li>
                        <b>Overall confidence:&nbsp;</b>
                        {h.booleanCheckbox(object.is_overall_confidence)}
                    </li>
                </ul>
            </div>
            <div className="col-md-8">
                <p>
                    <b>Description:&nbsp;</b>
                </p>
                <div dangerouslySetInnerHTML={{__html: object.description}}></div>
            </div>
        </div>
    );
};

DetailDomain.propTypes = {
    object: PropTypes.object.isRequired,
};
export default DetailDomain;
