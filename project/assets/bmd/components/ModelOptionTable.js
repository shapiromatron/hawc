import React from 'react';


class ModelOptionTable extends React.Component {

    handleCreateModel(){
        let modelName = $(this.refs.modelName).val();
        this.props.handleCreateModel(modelName);
    }

    handleRowClick(modelIndex){
        this.props.handleModalDisplay(modelIndex);
    }

    renderOption(d, i){
        return <option key={d} value={d}>{d}</option>;
    }

    renderOptionEdits(){
        if (!this.props.editMode) return;

        let {allOptions} = this.props;

        return (
            <div className='row-fluid' style={{marginBottom: '1em'}}>
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

    renderRow(d, i){
        let header = (this.props.editMode)?
             'View/edit': 'View';

        return (
            <tr key={i}>
                <td>{d}</td>
                <td></td>
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
                            <th style={{width: '30%'}}>Model name</th>
                            <th style={{width: '55%'}}>Non-default settings</th>
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
