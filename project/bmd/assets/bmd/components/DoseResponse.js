import React from 'react';
import PropTypes from 'prop-types';

class DoseResponse extends React.Component {
    componentDidMount() {
        let { endpoint } = this.props;
        endpoint.build_endpoint_table($(this.refs.epTable));
        endpoint.renderPlot($(this.refs.epFigure), false);
    }

    componentWillUnmount() {
        $(this.refs.epTable).empty();
        $(this.refs.epFigure).empty();
    }

    render() {
        return (
            <div>
                <h3>Dose-response</h3>
                <div className="row-fluid">
                    <div className="span8">
                        <table className="table table-condensed table-striped" ref="epTable" />
                    </div>
                    <div
                        className="span4"
                        style={{ height: '300px', width: '300px' }}
                        ref="epFigure"
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
