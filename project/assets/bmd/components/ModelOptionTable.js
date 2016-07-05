import React from 'react';


class ModelOptionTable extends React.Component {

    handleCreateModel(){
        console.log('handled');
    }

    handleToggleVariance(){
        console.log('handled');
    }

    renderOptionEdits(){
        if (!this.props.editMode) return;

        return (
            <div className='row-fluid' style={{marginBottom: '1em'}}>
                <label className="control-label">Add new model</label>
                <div className="controls">
                    <select style={{marginBottom: 0, marginRight: '1em'}}></select>
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
        // todo: only render if dataType == 'C'
        return (
            <button
                   onClick={this.handleToggleVariance.bind(this)}
                   type="button"
                   className='btn btn-small pull-right'
                   title='Change the variance model for all continuous models'
                   >Toggle all variance models</button>
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
                    </tbody>
                </table>
                {this.renderOptionEdits()}
            </div>
        );
    }
}

ModelOptionTable.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
};

export default ModelOptionTable;
