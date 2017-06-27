import React, { Component, PropTypes } from 'react';
import ReactQuill from 'react-quill';

import ScoreIcon from 'robTable/components/ScoreIcon';
import Select from 'shared/components/Select';
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
                10: '#FFCC00',
            },
            scoreChoices: {
                0: 'Not applicable',
                1: 'Critically deficient',
                2: 'Poor',
                3: 'Adequate',
                4: 'Good',
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
        // update notes if addText is modified
        // (usually by copying notes over from another form)
        if(nextProps.addText !== this.props.addText){
            this.setState({
                notes: this.state.notes + nextProps.addText,
            });
        }
        // if score notes is changed, change notes to new notes
        if(nextProps.score.notes !== this.props.score.notes){
            this.setState({
                notes: nextProps.score.notes,
            });
        }
        // if score is changed, change to new score
        if (nextProps.score.score !== this.props.score.score) {
            this.selectScore(nextProps.score.score);
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
        let { metric } = this.props.score.metric,
            { scoreChoices, score, notes, selectedSymbol, selectedShade } = this.state;
        return (
            <div className='score-form'>
                <div>
                    <Select choices={scoreChoices}
                          id={name}
                          value={score}
                          handleSelect={this.selectScore}/>
                    <br/><br/>
                    <ScoreIcon shade={selectedShade}
                             symbol={selectedSymbol}/>
                </div>
                <ReactQuill id={metric}
                         value={notes}
                         onChange={this.handleEditorInput}
                         toolbar={false}
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
            name: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
};

export default ScoreForm;
