import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

class Tooltip extends Component {
    render() {
        const style = {
                position: "absolute",
            },
            {x_filter} = this.props.datum;

        let x_filter_html = [];
        if (x_filter) {
            for (const key of _.keys(x_filter)) {
                x_filter_html.push(
                    <p>
                        {key}: {x_filter[key]}
                    </p>
                );
            }
        }

        return <div style={style}>{x_filter_html}</div>;
    }
}
Tooltip.propTypes = {
    datum: PropTypes.object,
};

export default Tooltip;
