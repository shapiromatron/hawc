import React, { PropTypes } from 'react';

const MetricSelect = (props) => {
    let { id, defVal, choices, handleSelect } = props;
    return (
         <select className='metric-select'
                    id={id}
                    ref='select'
                    defaultValue={defVal}
                    onChange={handleSelect}>
                {_.map(choices, (choice) => {
                    return <option key={choice.id} value={choice.id}>{choice.metric}</option>;
                })}
            </select>
    );
};

MetricSelect.propTypes = {
    handleSelect: PropTypes.func.isRequired,
    choices: PropTypes.array.isRequired,
    id: PropTypes.string.isRequired,
    defVal: PropTypes.any.isRequired,
};

export default MetricSelect;
