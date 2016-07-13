import React from 'react';

import {param_cw} from 'bmd/constants';


class ModelOptionTable extends React.Component {

    handleCreateModel(){
        let modelName = $(this.refs.modelName).val();
        this.props.handleCreateModel(modelName);
    }

    handleRowClick(modelIndex){
        this.props.handleModalDisplay(modelIndex);
    }

    renderOption(d, i){
        return <option key={i} value={i}>{d.name}</option>;
    }

    renderOptionEdits(){
        if (!this.props.editMode) return;

        let {allOptions} = this.props;

        return (
            <div className='row-fluid'>
                <label className="control-label">Add new model</label>
                <div className="controls">
                    <select
                        style={{marginBottom: 0, marginRight: '1em'}}
                        ref='modelName'>{allOptions.map(this.renderOption)}</select>
                    <button
                        onClick={this.handleCreateModel.bind(this)}
                        type="button"
                        className="btn btn-small"><i className="icon-plus"></i></button>
                    {this.renderToggleVarianceBtn()}
                </div>

            </div>
        );
    }

    renderToggleVarianceBtn(){
        if (this.props.dataType !== 'C'){
            return null;
        }

        return (
            <button
                   onClick={this.props.handleVarianceToggle}
                   type="button"
                   className='btn btn-small pull-right'
                   title='Change the variance model for all continuous models'
                   >Toggle all variance models</button>
        );
    }

    renderOverrideList(d){

        var getText = function(k, v){
            let def = d.defaults[k],
                tmp;
            switch (def.t){
            case 'i':
            case 'd':
            case 'dd':
            case 'rp':
                return <span><b>{def.n}:</b> {v}</span>;
            case 'b':
                tmp = (v===1) ? 'fa fa-check-square-o' :'fa fa-square-o';
                return <span><b>{def.n}:</b> <i className={tmp}></i></span>;
            case 'p':
                v = v.split('|');
                return <span><b>{def.n}:</b> {param_cw[v[0]]} to {v[1]}</span>;
            default:
                alert(`Invalid type: ${d.t}`);
                return null;
            }
        };

        if (_.isEmpty(d.overrides)){
            return <span>-</span>;
        } else {
            return <ul>{
                _.map(d.overrides, function(k, v){
                    return <li key={k}>{getText(v, k)}</li>;
                })
            }</ul>;
        }
    }

    renderRow(d, i){
        let header = (this.props.editMode)?'View/edit': 'View';


        return (
            <tr key={i}>
                <td>{d.name}</td>
                <td>
                    {this.renderOverrideList(d)}
                </td>
                <td>
                    <button
                        type="button"
                        className='btn btn-link'
                        onClick={this.handleRowClick.bind(this, i)}>{header}</button>
                </td>
            </tr>
        );
    }

    render() {
        let header = (this.props.editMode)?
             'View/edit': 'View';
        return (
            <div className="span6">
                <h4>Model options</h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th style={{width: '25%'}}>Model name</th>
                            <th style={{width: '60%'}}>Non-default settings</th>
                            <th style={{width: '15%'}}>{header}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.props.models.map(this.renderRow.bind(this))}
                    </tbody>
                </table>
                {this.renderOptionEdits()}
            </div>
        );
    }
}

ModelOptionTable.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    dataType: React.PropTypes.string.isRequired,
    handleVarianceToggle: React.PropTypes.func.isRequired,
    handleCreateModel: React.PropTypes.func.isRequired,
    handleModalDisplay: React.PropTypes.func.isRequired,
    models: React.PropTypes.array.isRequired,
    allOptions: React.PropTypes.array.isRequired,
};

export default ModelOptionTable;
