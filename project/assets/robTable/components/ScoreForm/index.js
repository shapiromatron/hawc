import React, { Component } from 'react';

import MyEditor from 'robTable/components/MyEditor';
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

    getScoreIcon(score){

    }

    render() {
        const { editorState } = this.state;
        return (
          <div className='score-form'>
              <span>Editor</span>
              <MyEditor />
          </div>
        );
    }
}

ScoreForm.propTypes = {
};

export default ScoreForm;
