import React, { Component, PropTypes } from 'react';
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
            score: null,
            notes: props.score.notes,
        };
        this.handleEditorInput = this.handleEditorInput.bind(this);
        this.selectScore = this.selectScore.bind(this);
    }

    componentWillMount(){
        this.selectScore(this.props.score.score);
    }

    componentWillUpdate(nextProps, nextState) {
        if(nextProps.addText !== this.props.addText){
            this.setState({
                notes: this.state.notes + nextProps.addText,
            });
        }
    }

    selectScore(score){
        this.setState({
            score,
            selectedShade: this.state.scoreShades[score],
            selectedSymbol: this.state.scoreSymbols[score],
        });
    }

    handleEditorInput(event){
        this.setState({notes: event});
    }

    render() {
        let { score } = this.props;

        return (
            <div className='score-form'>
                <div>
                    <Select choices={this.state.scoreChoices}
                          id={score.metric.metric}
                          defVal={score.score}
                          handleSelect={this.selectScore}/>
                    <br/><br/>
                    <ScoreIcon shade={this.state.selectedShade}
                             symbol={this.state.selectedSymbol}/>
                </div>
                <ReactQuill id={score.metric.metric}
                         value={this.state.notes}
                         onChange={this.handleEditorInput}
                         theme='snow'
                         className='score-editor' />
            </div>
        );
    }
}

ScoreForm.propTypes = {
    score: PropTypes.shape({
        score: PropTypes.number.isRequired,
        notes: PropTypes.string.isRequired,
        metric: PropTypes.shape({
            metric: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
};

export default ScoreForm;
