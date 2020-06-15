import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

class Tooltip extends Component {
    render() {
        const style = {
            position: "absolute",
        };

        let tooltip = null;

        if (this.props.type == "cell") tooltip = this.renderCellTooltip();
        if (this.props.type == "axis") tooltip = this.renderAxisTooltip();

        return <div style={style}>{tooltip}</div>;
    }

    renderCellTooltip() {
        const {x_filters, y_filters} = this.props.data,
            count = this.props.data.rows.length;
        let html = [];
        html.push(
            ...x_filters.map((e, i) => {
                let key = _.keys(e)[0];
                return (
                    <p key={`x_filter_${i}`}>
                        {key}: {e[key]}
                    </p>
                );
            })
        );
        html.push(
            ...y_filters.map((e, i) => {
                let key = _.keys(e)[0];
                return (
                    <p key={`y_filter_${i}`}>
                        {key}: {e[key]}
                    </p>
                );
            })
        );

        html.push(<p key="count">Count: {count}</p>);

        return html;
    }
    renderAxisTooltip() {
        const {filters} = this.props.data;
        let html = [];

        html.push(
            ...filters.map((e, i) => {
                let key = _.keys(e)[0];
                return (
                    <p key={`filter_${i}`}>
                        {key}: {e[key]}
                    </p>
                );
            })
        );

        return html;
    }
}
Tooltip.propTypes = {
    data: PropTypes.object,
    type: PropTypes.string,
};

export default Tooltip;
