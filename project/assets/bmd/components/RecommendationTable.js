import React from 'react';


class RecommendationTable extends React.Component {

    renderWarningTd(d){
        let tdId = '';

        if (this.props.selectedModelId-1 === d.id){ // TODO: change
            tdId = 'bmd_recommended_model';
        }

        if (this.props.selectedModelId === d.id){
            tdId = 'bmd_selected_model';
        }

        return (
            <td id={tdId}>{d.name}</td>
        );
    }

    renderRow(d, i){
        return (
            <tr key={i}>
                <td>{d.name}</td>
                <td>Recommendation</td>
                {this.renderWarningTd(d)}
            </tr>
        );
    }

    render(){
        return (
            <table className="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th style={{width: '15%'}}>Model</th>
                        <th style={{width: '60%'}}>Warnings</th>
                        <th style={{width: '25%'}}>Recommendation</th>
                    </tr>
                </thead>
                <tfoot>
                    <tr>
                        <td colSpan="3">
                            <ul>
                                <li>In the <b>Warnings</b> column, warnings for all models
                                are shown. Passed models are shown in green,
                                warnings in yellow, questionable in orange, and
                                failures in red.</li>

                                <li>In the <b>Recommendation</b> column, the recommended model
                                (if any) in green. The user-selected model (if any)
                                in yellow.</li>
                            </ul>
                        </td>
                    </tr>
                </tfoot>
                <tbody>
                    {this.props.models.map(this.renderRow.bind(this))}
                </tbody>
            </table>
        );
    }
}

RecommendationTable.propTypes = {
    models: React.PropTypes.array.isRequired,
    selectedModelId: React.PropTypes.number,
};

export default RecommendationTable;
