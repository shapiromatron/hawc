import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robTable/components/ScoreDisplay';

class CheckboxScoreDisplay extends Component {

    constructor(props) {
        super(props);
        this.state = {config: {
            display: 'final',
            isForm: false,
        }};
    }

    render() {
        return (
            <div>
                <ScoreDisplay />
                <input type="checkbox"
                       title="Include/exclude selected item in change"
                       checked={checked}
                       id={item.id}
                       onChange={this.props.checkItem}/>
            </div>
        );
    }
}

CheckboxScoreDisplay.propTypes = {
    checkItem: PropTypes.func.isRequired,
    item: PropTypes.shape({
        notes: PropTypes.string,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
    }),
};

export default CheckboxScoreDisplay;
