import React, { PropTypes } from 'react';
import ReactDOM from 'react-dom';

import ScoreDisplay from 'robTable/components/ScoreDisplay';

const CrossStudyDisplay = (props) => {
    let { domain, metric, scores } = props;
    scores = scores[0].values[0].values;
    return (
        <div className='cross-study-display'>
            <h3>{domain}</h3>
            <h4>{metric.metric}</h4>
            <div className='help-block'>
                {metric.description}
            </div>
            {_.map(scores, (rob, i) => {
                return (
                    <div key={rob.id}>
                        <h4><a target='_blank' href={rob.study.url}>
                            {rob.study.name}
                        </a></h4>
                        <ScoreDisplay key={i} score={rob} />
                    </div>
                );
            })}

        </div>
    );
};

export function renderCrossStudyDisplay(data, element){
    return ReactDOM.render(<CrossStudyDisplay {...data} />, element);
}

export default CrossStudyDisplay;
