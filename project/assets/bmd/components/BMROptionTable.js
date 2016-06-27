import React from 'react';


class BMROptionTable extends React.Component {

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
            </div>
        );
    }
}

BMROptionTable.propTypes = {
    editMode: React.PropTypes.bool,
};

export default BMROptionTable;
