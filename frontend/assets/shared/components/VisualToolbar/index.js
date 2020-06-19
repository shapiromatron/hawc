import React, {Component} from "react";
import PropTypes from "prop-types";
import d3 from "d3";

const getSvgObject = function(svgElement) {
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: http://nytimes.github.com/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.
        const get_selected_svg = function(svg) {
                svg.attr("version", "1.1");
                svg.attr("xmlns", d3.ns.prefix.svg);
                var source = new XMLSerializer().serializeToString(svg.node()),
                    rect = svg.node().getBoundingClientRect();
                return {
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height,
                    classes: svg.attr("class"),
                    id: svg.attr("id"),
                    childElementCount: svg.node().childElementCount,
                    source: [source],
                };
            },
            svg = d3.select(svgElement),
            svg_object = get_selected_svg(svg);

        svg_object.blob = new Blob(svg_object.source, {type: "text/xml"});
        return svg_object;
    },
    downloadImage = function(svgElement, format) {
        event.preventDefault();
        var svg_blob = getSvgObject(svgElement);
        $(
            `<form style="display: none;" action="/assessment/download-plot/" method="post">
                <input name="height" value="${svg_blob.height}">
                <input name="width" value="${svg_blob.width}">
                <input name="svg" value="${btoa(escape(svg_blob.source[0]))}">
                <input name="output" value="${format}">
            </form>`
        )
            .appendTo("body")
            .submit();
    };

class VisualToolbar extends Component {
    renderDownload() {
        const {svg} = this.props;
        return (
            <div className="btn-group dropup" title="Download image">
                <button className="btn btn-mini dropdown-toggle" data-toggle="dropdown">
                    <i className="fa fa-download"></i>
                </button>
                <ul className="dropdown-menu pull-right">
                    <li>
                        <a href="#" onClick={() => downloadImage(svg, "svg")}>
                            <i className="fa fa-picture-o"></i>&nbsp;Download SVG
                        </a>
                        <a href="#" onClick={() => downloadImage(svg, "pptx")}>
                            <i className="fa fa-file-powerpoint-o"></i>&nbsp;Download PPTX
                        </a>
                        <a href="#" onClick={() => downloadImage(svg, "pdf")}>
                            <i className="fa fa-file-pdf-o"></i>&nbsp;Download PDF
                        </a>
                        <a href="#" onClick={() => downloadImage(svg, "png")}>
                            <i className="fa fa-picture-o"></i>&nbsp;Download PNG
                        </a>
                    </li>
                </ul>
            </div>
        );
    }
    renderZoom() {
        return (
            <button className="btn btn-mini" title="Zoom in/out">
                <i className="fa fa-search-plus"></i>
            </button>
        );
    }
    render() {
        return (
            <div className="pull-right">
                {this.renderZoom()}
                {this.renderDownload()}
            </div>
        );
    }
}

VisualToolbar.propTypes = {
    svg: PropTypes.object.isRequired,
};

export default VisualToolbar;
