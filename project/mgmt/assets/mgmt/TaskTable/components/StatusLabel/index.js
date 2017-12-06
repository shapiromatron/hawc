import React from 'react';
import PropTypes from 'prop-types';

import h from 'mgmt/utils/helpers';
import StatusIcon from 'mgmt/TaskTable/components/StatusIcon';

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
