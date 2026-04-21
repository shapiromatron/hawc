import React from "react";
import Alert from "shared/components/Alert";

class UnderDevelopment extends React.Component {
    render() {
        return (
            <Alert
                className="alert-warning mb-2"
                icon="fa-question-circle"
                message={
                    <span>
                        This feature is actively under development. It is not yet stable, and there
                        may be breaking changes in the future. Please{" "}
                        <a href="/contact/">contact us</a> with any issues or suggestions for
                        improvement.
                    </span>
                }
            />
        );
    }
}

export default UnderDevelopment;
