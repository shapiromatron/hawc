import StatusIcon from "mgmt/TaskTable/components/StatusIcon";
import PropTypes from "prop-types";
import React from "react";
import h from "shared/utils/helpers";

const StatusLabel = props => {
    return (
        <div>
            <b>Status: </b>
            <StatusIcon status={props.task.status} />
            {h.caseToWords(props.task.status_display)}
        </div>
    );
};

StatusLabel.propTypes = {
    task: PropTypes.shape({
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
    }).isRequired,
};

export default StatusLabel;
