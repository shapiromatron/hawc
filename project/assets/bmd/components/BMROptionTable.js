import React from 'react';


class BMROptionTable extends React.Component {

    handleRowClick(bmrIndex){
        this.props.handleModalDisplay(bmrIndex);
    }

    renderEditDiv(){
        if (!this.props.editMode) return;

        return (
            <div className='row-fluid' >
                <div className="controls">
                    <button
                        onClick={this.props.handleCreateBmr}
                        type="button"
                        className="btn btn-small pull-right">
                            <i className="icon-plus"></i> Create new BMR</button>
                </div>
            </div>
        );
    }

    renderRow(d, i){
        let header = (this.props.editMode)?
             'View/edit': 'View';

        return (
            <tr key={i}>
                <td>{d.name}</td>
                <td></td>
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
                        {this.props.bmrs.map(this.renderRow.bind(this))}
                    </tbody>
                </table>
                {this.renderEditDiv()}
            </div>
        );
    }
}

BMROptionTable.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    handleCreateBmr: React.PropTypes.func.isRequired,
    handleModalDisplay: React.PropTypes.func.isRequired,
    bmrs: React.PropTypes.array.isRequired,
    allOptions: React.PropTypes.array.isRequired,
};

export default BMROptionTable;
