import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robTable/components/ScoreDisplay';
import './CheckboxScoreDisplay.css';

class CheckboxScoreDisplay extends Component {

    constructor(props) {
        super(props);
        this.state = {
            config: {
                display: 'final',
                isForm: false,
        }};
    }

    render() {
        let { checked, item, config, handleCheck } = this.props;
        return (
            <div className='flexRow-container'>
                <input className='score-display-checkbox'
                       type="checkbox"
                       title="Include/exclude selected item in change"
                       checked={checked}
                       id={item.id}
                       onChange={handleCheck}/>
                <ScoreDisplay key={item.id} score={item} config={config} />
            </div>
        );
    }
}

CheckboxScoreDisplay.propTypes = {
    handleCheck: PropTypes.func.isRequired,
    item: PropTypes.shape({
        id: PropTypes.number.isRequired,
        notes: PropTypes.string,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
    }),
    config: PropTypes.object.isRequired,
};

export default CheckboxScoreDisplay;
