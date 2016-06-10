import React, { Component, PropTypes } from 'react';

import ScoreBar from 'robTable/components/ScoreBar';
import './ScoreDisplay.css';


class ScoreDisplay extends Component {

    constructor(props) {
        super(props);
        // values of state.flex correspond to css classes in flex.css
        this.state = {flex: 'flexRow'};
        this.toggleWidth = 600;
        this.checkFlex = this.checkFlex.bind(this);
    }


    // sets state.flex based on the width of the component.
    checkFlex() {
        if (this.state.flex === 'flexRow' && this.refs.display.offsetWidth <= this.toggleWidth){
            this.setState({flex: 'flexColumn'});
        } else if (this.state.flex === 'flexColumn' && this.refs.display.offsetWidth > this.toggleWidth){
            this.setState({flex: 'flexRow'});
        }
    }

    componentDidMount() {
        this.checkFlex();
        window.addEventListener('resize', this.checkFlex);
    }

    componentWillUnmount(nextProps, nextState) {
        window.removeEventListener('resize', this.checkFlex);
    }

    render(){
        let { score } = this.props;
        return (
            <div className='score-display'>
                <h5>{score.author.full_name}</h5>
                <ScoreBar score={score.score}
                          shade={score.score_shade}
                          symbol={score.score_symbol}
                          description={score.score_description}/>
                <hr/>
                <span dangerouslySetInnerHTML={{
                    __html: score.notes,
                }} />
            </div>
        );
    }
}

ScoreDisplay.propTypes = {
    score: PropTypes.shape({
        author: PropTypes.object.isRequired,
        domain_id: PropTypes.number,
        domain_text: PropTypes.string,
        metric: PropTypes.shape({
            description: PropTypes.string.isRequired,
            metric: PropTypes.string.isRequired,
        }).isRequired,
        notes: PropTypes.string,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
    }).isRequired,
};

export default ScoreDisplay;
