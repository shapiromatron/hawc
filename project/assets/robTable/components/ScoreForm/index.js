import React, { Component } from 'react';

import './ScoreForm.css';


class ScoreForm extends Component {

    constructor(props){
        super(props);
        this.state = {
            scoreText: {0: 'N/A', 1: '--', 2: '-', 3: '+', 4: '++'},
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

    selectScore(e){
        let score = e.target.value;
        this.scoreSymbol = this.state.scoreShades[score];
        this.scoreColor = this.state.scoreText[score];
    }

    render() {
        let { score } = this.props;
        this.scoreColor = score.score_shade;
        this.scoreSymbol = score.score_symbol;

        return (
          <div className='score-form'>
              <div>
                  <select name="score-select"
                          id={score.metric.metric}
                          defaultValue={score.score}
                          onChange={this.selectScore}>
                      {_.map(this.state.scoreChoices, (score, key) => {
                          return <option value={key}>{score}</option>;
                      })}
                  </select>
                  <br/><br/>
                  <div className='score-icon' style={{backgroundColor: this.scoreColor}}>{this.scoreSymbol}</div>
              </div>
              <textarea name={`${score.metric.metric}-text`} id={score.metric.metric} cols='40' rows="8"></textarea>
          </div>
        );
    }
}

ScoreForm.propTypes = {
};

export default ScoreForm;
