import React, { Component } from 'react';
import PropTypes from 'prop-types';

import h from 'riskofbias/robScoreCleanup/utils/helpers';
import ScoreDisplay from 'riskofbias/robTable/components/ScoreDisplay';
import Study from 'study/Study';
import './CheckboxScoreDisplay.css';

class CheckboxScoreDisplay extends Component {

    render() {
        let { checked, item, config, handleCheck } = this.props,
            scoreInfo = h.getScoreInfo(item.score);
        item = {...item, score_shade: scoreInfo.shade, score_description: scoreInfo.text};
        return (
            <div className='flexRow-container'>
                <div className='score-display-checkbox'>
                    <p onClick={() => { Study.displayAsModal(item.study_id); }}><b>{item.study_name}</b></p>
                    <input type="checkbox"
                        title="Include/exclude selected item in change"
                        checked={checked}
                        id={item.id}
                        onChange={handleCheck}/>
                </div>
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
