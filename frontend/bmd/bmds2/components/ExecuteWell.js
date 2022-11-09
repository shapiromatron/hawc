import PropTypes from "prop-types";
import React from "react";

class ExecuteWell extends React.Component {
    render() {
        const {editMode, isExecuting, handleExecute, validationErrors} = this.props;

        if (!editMode) {
            return null;
        }
        return (
            <div className="well" style={{marginTop: "1em"}}>
                {isExecuting ? null : (
                    <button type="button" className="btn btn-primary" onClick={handleExecute}>
                        Execute
                    </button>
                )}
                {isExecuting ? (
                    <p>
                        <b>BMD executing, please wait...</b>
                        <i className="fa fa-spinner fa-spin fa-3x fa-fw" />
                    </p>
                ) : null}
                {validationErrors.length > 0 ? (
                    <div className="alert alert-danger" style={{marginTop: "1em"}}>
                        <b>The following validation warnings were found:</b>
                        <ul>
                            {validationErrors.map((d, i) => {
                                return <li key={i}>{d}</li>;
                            })}
                        </ul>
                    </div>
                ) : null}
            </div>
        );
    }
}

ExecuteWell.propTypes = {
    editMode: PropTypes.bool.isRequired,
    handleExecute: PropTypes.func.isRequired,
    validationErrors: PropTypes.array.isRequired,
    isExecuting: PropTypes.bool.isRequired,
};

export default ExecuteWell;
