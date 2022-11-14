import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

class TableauDashboard extends Component {
    /*
    Use the recommended approach for embedding a tableau dashboard into an application. For
    developer documentation, see:
        https://help.tableau.com/current/pro/desktop/en-us/embed_list.htm
    */
    componentDidMount() {
        // inject tableau script
        const head = document.querySelector("head"),
            script = document.createElement("script");

        script.setAttribute("src", "https://public.tableau.com/javascripts/api/viz_v1.js");
        head.appendChild(script);
    }

    render() {
        const {hostUrl, path, queryArgs} = this.props,
            contentSize = h.getHawcContentSize(),
            MIN_HEIGHT = 600,
            MIN_WIDTH = 700,
            height = Math.max(contentSize.height, MIN_HEIGHT),
            width = Math.max(contentSize.width, MIN_WIDTH);

        let fullPath = queryArgs && queryArgs.length > 0 ? `${path}?${queryArgs.join("&")}` : path;

        return (
            <object
                className="tableauViz"
                height={`${height}px`}
                width={`${width}px`}
                style={{display: "none"}}>
                <param name="host_url" value={hostUrl} />
                <param name="path" value={fullPath} />
                <param name="toolbar" value="yes" />
                <param name="display_spinner" value="yes" />
            </object>
        );
    }
}

TableauDashboard.propTypes = {
    hostUrl: PropTypes.string.isRequired,
    path: PropTypes.string.isRequired,
    queryArgs: PropTypes.arrayOf(PropTypes.string),
};

export default TableauDashboard;
