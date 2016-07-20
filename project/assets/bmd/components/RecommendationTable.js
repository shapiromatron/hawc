import _ from 'underscore';
import React from 'react';

import {asLabel} from 'bmd/models/bmr';


class RecommendationTable extends React.Component {

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
            <form className="form-horizontal">

                <div className="control-group form-row">
                    <label for="bmr"
                           className="control-label">Selected BMR</label>
                    <div className="controls">
                        <select
                            value={this.state.bmr}
                            name='bmr'
                            onChange={this.handleFieldChange.bind(this)}>
                        {this.props.bmrs.map((d, i)=>{
                            return <option key={i} value={i}>{asLabel(d)}</option>;
                        })}
                        </select>
                    </div>
                </div>

                <div className="control-group form-row">
                    <label for="model"
                           className="control-label">Selected model</label>
                    <div className="controls">
                        <select
                            value={this.state.model}
                            name='model'
                            onChange={this.handleFieldChange.bind(this)}>
                        {models.map((d)=>{
                            return <option key={d.id} value={d.id}>{d.name}</option>;
                        })}
                        </select>
                    </div>
                </div>

                <div className="control-group form-row">
                    <label for="notes"
                           className="control-label">Notes</label>
                    <div className="controls">
                        <textarea
                            value={this.state.notes}
                            onChange={this.handleFieldChange.bind(this)}
                            name='notes'
                            rows="5"
                            cols="40"></textarea>
                    </div>
                </div>

            </form>
        );
    }

    renderTable(){
        return (
            <table className="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th style={{width: '20%'}}>Description</th>
                        <th style={{width: '70%'}}>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Model</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Override</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Notes</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
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
        return (
            <div>
                {this.renderTable()}
                {this.renderForm()}
                {this.renderWell()}
            </div>
        );
    }
}

RecommendationTable.propTypes = {
    selectedModelId: React.PropTypes.number,
    selectedModelNotes: React.PropTypes.string.isRequired,
    handleSaveSelected: React.PropTypes.func.isRequired,
    models: React.PropTypes.array.isRequired,
    bmrs: React.PropTypes.array.isRequired,
};

export default RecommendationTable;
