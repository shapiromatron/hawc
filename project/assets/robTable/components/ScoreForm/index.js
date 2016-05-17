import React, { Component } from 'react';

import './ScoreForm.css';


class ScoreForm extends Component {

    constructor(props){
        super(props);
        this.state = {
            scoreSymbols: {0: 'N/A', 1: '--', 2: '-', 3: '+', 4: '++'},
            scoreShades: {
                0: '#E8E8E8',
                1: '#CC3333',
                2: '#FFCC00',
                3: '#6FFF00',
                4: '#00CC00',
            },
            scoreChoices: {
                0: 'Not applicable',
                1: 'Definitely high risk-of-bias',
                2: 'Probably high risk-of-bias',
                3: 'Probably low risk-of-bias',
                4: 'Definitely low risk-of-bias',
            },
        };
    }

    componentWillMount(){
        let { score } = this.props;
        this.setState({
            selectedShade: this.state.scoreShades[score.score],
            selectedSymbol: this.state.scoreSymbols[score.score],
        });
    }

    selectScore(e){
        let selectedScore = e.target.value;
        this.setState({
            selectedShade: this.state.scoreShades[selectedScore],
            selectedSymbol: this.state.scoreSymbols[selectedScore],
        });
    }

    render() {
        let { score } = this.props;

        return (
          <div className='score-form'>
              <div>
                  <select name="score-select"
                          id={score.metric.metric}
                          defaultValue={score.score}
                          onChange={this.selectScore.bind(this)}>
                      {_.map(this.state.scoreChoices, (score, key) => {
                          return <option key={key} value={key}>{score}</option>;
                      })}
                  </select>
                  <br/><br/>
                  <div className='score-icon'
                      style={{backgroundColor: this.state.selectedShade}}>
                          {this.state.selectedSymbol}
                  </div>
              </div>
              <textarea name={`${score.metric.metric}-text`} id={score.metric.metric} cols='40' rows="8"></textarea>
          </div>
        );
    }
}

ScoreForm.propTypes = {
};

export default ScoreForm;
