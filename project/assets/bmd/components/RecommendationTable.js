import React from 'react';


class RecommendationTable extends React.Component {

    renderForm(){
        return (
            <form className="form-horizontal">

                <div className="control-group form-row">
                    <label for="selected_model"
                           className="control-label">Selected model</label>
                    <div className="controls">
                        <select
                            id="selected_model"
                            name="selected_model"></select>
                    </div>
                </div>

                <div className="control-group form-row">
                    <label for="override_notes"
                           className="control-label">Notes</label>
                    <div className="controls">
                        <textarea id="override_notes"
                            name="override_notes"
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
                        onClick={this.props.handleSaveSelected}>Save selected model</button>
            </div>
        );
    }

    render() {
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
    handleSaveSelected: React.PropTypes.func.isRequired,
};

export default RecommendationTable;
