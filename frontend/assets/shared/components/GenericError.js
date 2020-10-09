import React from "react";

class GenericError extends React.Component {
    render() {
        return (
            <div className="alert alert-danger">
                <i className="fa fa-exclamation-triangle"></i>&nbsp; An error ocurred. If the error
                continues to occur please contact us.
            </div>
        );
    }
}

export default GenericError;
