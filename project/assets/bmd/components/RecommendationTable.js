import React from 'react';


class RecommendationTable extends React.Component {

    render() {
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
}

RecommendationTable.propTypes = {
};

export default RecommendationTable;
