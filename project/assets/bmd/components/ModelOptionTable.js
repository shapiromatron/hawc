import React from 'react';


class ModelOptionTable extends React.Component {

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
            </div>
        );
    }
}

ModelOptionTable.propTypes = {
    editMode: React.PropTypes.bool,
};

export default ModelOptionTable;
