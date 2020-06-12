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

        for (const filter of x_filters) {
            html.push(
                <p>
                    {filter[0]}: {filter[1]}
                </p>
            );
        }
        for (const filter of y_filters) {
            html.push(
                <p>
                    {filter[0]}: {filter[1]}
                </p>
            );
        }
        html.push(<p>Count: {count}</p>);

        return html;
    }
    renderAxisTooltip() {
        const {filters} = this.props.data;
        let html = [];

        for (const filter of filters) {
            html.push(
                <p>
                    {filter[0]}: {filter[1]}
                </p>
            );
        }

        return html;
    }
}
Tooltip.propTypes = {
    data: PropTypes.object,
    type: PropTypes.string,
};

export default Tooltip;
