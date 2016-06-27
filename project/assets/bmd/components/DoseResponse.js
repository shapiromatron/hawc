import React from 'react';


class DoseResponse extends React.Component {

    render() {
        return (
            <div>
                <h3>Dose-response</h3>
                <div className="row-fluid">
                    <div className="span8">
                        <p>Table</p>
                        <table className="table table-condensed table-striped">
                        </table>
                    </div>
                    <div className="span4">
                        <p>Figure</p>
                    </div>
                </div>
            </div>
        );
    }
}

DoseResponse.propTypes = {
};

export default DoseResponse;
