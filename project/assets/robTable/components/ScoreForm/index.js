import React, { Component } from 'react';
import ReactQuill from 'react-quill';
import '../../../../node_modules/quill/dist/quill.base.css';
import '../../../../node_modules/quill/dist/quill.snow.css';

import ScoreIcon from 'robTable/components/ScoreIcon';
import Select from 'robTable/components/Select';
import './ScoreForm.css';


class ScoreForm extends Component {

    constructor(props){
        super(props);
        this.state = {
            scoreSymbols: {0: 'N/A', 1: '--', 2: '-', 3: '+', 4: '++', 10: 'NR'},
            scoreShades: {
                0: '#E8E8E8',
                1: '#CC3333',
                2: '#FFCC00',
                3: '#6FFF00',
                4: '#00CC00',
                10: '#E8E8E8',
            },
            scoreChoices: {
                0: 'Not applicable',
                1: 'Definitely high risk of bias',
                2: 'Probably high risk of bias',
                3: 'Probably low risk of bias',
                4: 'Definitely low risk of bias',
                10: 'Not reported',
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

    selectScore(score){
        this.setState({
            selectedShade: this.state.scoreShades[score],
            selectedSymbol: this.state.scoreSymbols[score],
        });
    }

    render() {
        let { score } = this.props;

        return (
          <div className='score-form'>
              <div>
                  <Select choices={this.state.scoreChoices}
                          id={score.metric.metric}
                          defVal={score.score}
                          ref='score'
                          handleSelect={this.selectScore.bind(this)}/>
                  <br/><br/>
                  <ScoreIcon shade={this.state.selectedShade}
                             symbol={this.state.selectedSymbol}/>
              </div>
              <ReactQuill ref='notes'
                          id={score.metric.metric}
                          defaultValue={score.notes}
                          theme='snow'
                          className='score-editor' />
          </div>
        );
    }
}

ScoreForm.propTypes = {
};

export default ScoreForm;
