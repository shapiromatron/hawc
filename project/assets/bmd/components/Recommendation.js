import _ from 'underscore';
import React from 'react';

import {asLabel} from 'bmd/models/bmr';

import RecommendationTable from './RecommendationTable';


class Recommendation extends React.Component {

    updateState(props){
        let model = (props.selectedModelId) ?
                _.findWhere(props.models, {id: props.selectedModelId}):
                props.models[0],
            d = {
                bmr: model.bmr_id,
                model: model.id,
                notes: props.selectedModelNotes,
            };
        this.setState(d);
    }

    componentWillMount(){
        this.updateState(this.props);
    }

    componentWillReceiveProps(nextProps){
        this.updateState(nextProps);
    }

    handleFieldChange(e){
        let d={},
            name = e.target.name,
            val = e.target.value;

        if (_.contains(['bmr', 'model'], name)){
            val = parseInt(val);
        }

        d[name] = val;
        this.setState(d);
    }

    handleSaveSelected(){
        this.props.handleSaveSelected(this.state.model, this.state.notes);
    }

    renderForm(){
        let models = _.where(
            this.props.models,
            {bmr_id: this.state.bmr}
        );

        return (
            <div className='row-fluid'>
            <legend>Select BMD model</legend>
            <form className="form">
                <div className='span4'>
                    <label for="bmr"
                           className="control-label">Selected BMR</label>
                    <div className="controls">
                        <select
                            className='span12'
                            value={this.state.bmr}
                            name='bmr'
                            onChange={this.handleFieldChange.bind(this)}>
                        {this.props.bmrs.map((d, i)=>{
                            return <option key={i} value={i}>{asLabel(d)}</option>;
                        })}
                        </select>
                    </div>

                    <label for="model"
                           className="control-label">Selected model</label>

                    <div className="controls">
                        <select
                            className='span12'
                            value={this.state.model}
                            name='model'
                            onChange={this.handleFieldChange.bind(this)}>
                        {models.map((d)=>{
                            return <option key={d.id} value={d.id}>{d.name}</option>;
                        })}
                        </select>
                    </div>
                </div>
                <div className='span8'>
                    <label for="notes"
                           className="control-label">Notes</label>
                    <div className="controls">
                        <textarea
                            className='span12'
                            value={this.state.notes}
                            onChange={this.handleFieldChange.bind(this)}
                            name='notes'
                            rows="5"
                            cols="40"></textarea>
                    </div>
                </div>
            </form>
            </div>
        );
    }

    renderWell(){
        return (
            <div className='well'>
                <button type='button'
                        className='btn btn-primary'
                        onClick={this.handleSaveSelected.bind(this)}>Save selected model</button>
            </div>
        );
    }

    render() {
        if (this.props.models.length===0){
            return null;
        }

        let modelSubset = _.where(
            this.props.models,
            {bmr_id: this.state.bmr}
        );

        return (
            <div>
                <RecommendationTable
                    models={modelSubset}
                    selectedModelId={this.props.selectedModelId} />
                {this.renderForm()}
                {this.renderWell()}
            </div>
        );
    }
}

Recommendation.propTypes = {
    selectedModelId: React.PropTypes.number,
    selectedModelNotes: React.PropTypes.string.isRequired,
    handleSaveSelected: React.PropTypes.func.isRequired,
    models: React.PropTypes.array.isRequired,
    bmrs: React.PropTypes.array.isRequired,
};

export default Recommendation;
