import React from "react";
import PropTypes from "prop-types";

class DoseResponse extends React.Component {
    constructor(props) {
        super(props);
        this.epTable = React.createRef();
        this.epFigure = React.createRef();
    }

    componentDidMount() {
        let {endpoint} = this.props;
        endpoint.build_endpoint_table($(this.epTable.current));
        endpoint.renderPlot($(this.epFigure.current), {showBmd: false});
    }

    componentWillUnmount() {
        $(this.epTable.current).empty();
        $(this.epFigure.current).empty();
    }

    render() {
        return (
            <div>
                <h3>Dose-response</h3>
                <div className="row">
                    <div className="col-md-8">
                        <table className="table table-sm table-striped" ref={this.epTable} />
                    </div>
                    <div
                        className="col-md-4"
                        style={{height: "300px", width: "300px"}}
                        ref={this.epFigure}
                    />
                </div>
            </div>
        );
    }
}

DoseResponse.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

export default DoseResponse;
