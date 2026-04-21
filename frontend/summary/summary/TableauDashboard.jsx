import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

class TableauDashboard extends Component {
    /*
    Use the recommended approach for embedding a tableau dashboard into an application. For
    developer documentation, see:
        https://help.tableau.com/current/api/embedding_api/en-us/index.html
    */
    componentDidMount() {
        // inject tableau script
        const head = document.querySelector("head"),
            script = document.createElement("script");

        script.setAttribute(
            "src",
            "https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js"
        );
        script.setAttribute("type", "module");
        head.appendChild(script);
    }

    render() {
        const {hostUrl, path, queryArgs, filters} = this.props,
            contentSize = h.getHawcContentSize(),
            MIN_HEIGHT = 600,
            MIN_WIDTH = 700,
            height = Math.max(contentSize.height, MIN_HEIGHT),
            width = Math.max(contentSize.width, MIN_WIDTH);

        let fullPath = queryArgs && queryArgs.length > 0 ? `${path}?${queryArgs.join("&")}` : path;

        return (
            <tableau-viz src={hostUrl + fullPath} height={height} width={width} class="tableau-viz">
                {filters.map((filter, i) => {
                    return (
                        <viz-filter key={i} field={filter.field} value={filter.value}></viz-filter>
                    );
                })}
            </tableau-viz>
        );
    }
}

TableauDashboard.propTypes = {
    hostUrl: PropTypes.string.isRequired,
    path: PropTypes.string.isRequired,
    queryArgs: PropTypes.arrayOf(PropTypes.string),
    filters: PropTypes.arrayOf(
        PropTypes.shape({field: PropTypes.string.isRequired, value: PropTypes.string.isRequired})
    ),
};

export default TableauDashboard;
