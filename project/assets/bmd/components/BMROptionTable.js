import React from 'react';


class BMROptionTable extends React.Component {

    handleCreate(){
        console.log('handled');
    }

    renderEditDiv(){
        if (!this.props.editMode) return;

        return (
            <div className='row-fluid' style={{marginBottom: '1em'}}>
                <label className="control-label">Add new BMR</label>
                <div className="controls">
                    <select style={{marginBottom: 0, marginRight: '1em'}}></select>
                    <button
                        onClick={this.handleCreate.bind(this)}
                        type="button"
                        className="btn btn-small"><i className="icon-plus"></i></button>
                </div>
            </div>
        );
    }


    render() {
        let header = (this.props.editMode)?
             'View/edit': 'View';
        return (
            <div className="span6">
                <h4>Benchmark modeling responses</h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th style={{width:'30%'}}>Type</th>
                            <th style={{width:'20%'}}>Value</th>
                            <th style={{width:'25%'}}>Confidence level</th>
                            <th style={{width:'25%'}}>{header}</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <td colSpan="4">
                            All models will be run using the selected BMRs,
                            if appropriate for that particular model type.
                            </td>
                        </tr>
                    </tfoot>
                    <tbody>
                    </tbody>
                </table>
                {this.renderEditDiv()}
            </div>
        );
    }
}

BMROptionTable.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
};

export default BMROptionTable;
