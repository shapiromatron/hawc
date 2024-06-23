import React from "react";

class Loading extends React.Component {
    render() {
        return (
            <div className="is-loading">
                <p>
                    Loading, please wait...&nbsp;
                    <span className="fa fa-spin fa-spinner" />
                </p>
            </div>
        );
    }
}

export default Loading;
