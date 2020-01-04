import React, { Component } from 'react';
import PropTypes from 'prop-types';

import h from 'shared/utils/helpers';
import ScoreBar from 'riskofbias/robTable/components/ScoreBar';
import './ScoreDisplay.css';

class ScoreDisplay extends Component {
    constructor(props) {
        super(props);
        // values of state.flex correspond to css classes in flex.css
        this.state = { flex: 'flexRow' };
        this.toggleWidth = 650;
        this.checkFlex = this.checkFlex.bind(this);
        this.copyNotes = this.copyNotes.bind(this);
    }

    componentDidMount() {
        this.checkFlex();
        window.addEventListener('resize', this.checkFlex);
    }

    componentWillUnmount(nextProps, nextState) {
        window.removeEventListener('resize', this.checkFlex);
    }

    // sets state.flex based on the width of the component.
    checkFlex() {
        if (this.state.flex === 'flexRow' && this.refs.display.offsetWidth <= this.toggleWidth) {
            this.setState({ flex: 'flexColumn' });
        } else if (
            this.state.flex === 'flexColumn' &&
            this.refs.display.offsetWidth > this.toggleWidth
        ) {
            this.setState({ flex: 'flexRow' });
        }
    }

    copyNotes(e) {
        e.preventDefault();
        this.props.copyNotes(this.props.score.notes);
    }

    render() {
        let { score, config } = this.props,
            copyTextButton = this.props.copyNotes ? (
                <button className="btn btn-secondary copy-notes" onClick={this.copyNotes}>
                    Copy Notes
                </button>
            ) : null;
        if (h.hideRobScore(score.metric.domain.assessment.id)) {
            return (
                <div className={`score-display ${this.state.flex}-container`} ref="display">
                    <div className="flex-3 score-notes">
                        <div
                            dangerouslySetInnerHTML={{
                                __html: score.notes,
                            }}
                        />
                        {copyTextButton}
                    </div>
                </div>
            );
        }
        return (
            <div className={`score-display ${this.state.flex}-container`} ref="display">
                <div className="flex-1">
                    {config.display === 'final' && !config.isForm ? null : (
                        <p>
                            <b>{score.author.full_name}</b>
                        </p>
                    )}
                    <ScoreBar
                        score={score.score}
                        shade={score.score_shade}
                        symbol={score.score_symbol}
                        description={score.score_description}
                    />
                </div>
                <div className="flex-3 score-notes">
                    <div
                        dangerouslySetInnerHTML={{
                            __html: score.notes,
                        }}
                    />
                    {copyTextButton}
                </div>
            </div>
        );
    }
}

ScoreDisplay.propTypes = {
    score: PropTypes.shape({
        author: PropTypes.object.isRequired,
        notes: PropTypes.string,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
        score: PropTypes.number.isRequired,
    }).isRequired,
    config: PropTypes.object.isRequired,
    copyNotes: PropTypes.func,
};

export default ScoreDisplay;
