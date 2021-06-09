import React from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

const DetailMetric = props => {
    const {object} = props;
    return (
        <div className="row mr-1" style={{maxHeight: 300, overflowY: "auto"}}>
            <div className="col-md-4">
                <ul>
                    <li>
                        <b>Name:&nbsp;</b>
                        {object.name}
                    </li>
                    <li>
                        <b>Short name:&nbsp;</b>
                        {object.short_name}
                    </li>
                    <li>
                        <b>Required animal:&nbsp;</b>
                        {h.booleanCheckbox(object.required_animal)}
                    </li>
                    <li>
                        <b>Required epi:&nbsp;</b>
                        {h.booleanCheckbox(object.required_epi)}
                    </li>
                    <li>
                        <b>Required invitro:&nbsp;</b>
                        {h.booleanCheckbox(object.required_invitro)}
                    </li>
                    <li>
                        <b>Hide description:&nbsp;</b>
                        {h.booleanCheckbox(object.hide_description)}
                    </li>
                    <li>
                        <b>Use short name:&nbsp;</b>
                        {h.booleanCheckbox(object.use_short_name)}
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

DetailMetric.propTypes = {
    object: PropTypes.object.isRequired,
};

export default DetailMetric;
