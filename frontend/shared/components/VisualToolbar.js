import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import * as d3 from "d3";
import {action, computed, observable} from "mobx";
import {observer} from "mobx-react";

/*
Utility toolbelt for visualizations. Adds a few key attributes:

1) adds ability to download SVG
2) adds resizing button and triggering (note that this has side-effects)

Note that creating an instances registers an listener on window resize that is not currently
cleaned up after being destroyed.

*/

const getSvgObject = function(svgElement) {
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: http://nytimes.github.com/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.
        const get_selected_svg = function(svg) {
                svg.attr("version", "1.1");
                svg.attr("xmlns", d3.namespaces.svg);
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
    },
    getDomSize = $el => {
        return {width: $el.width(), height: $el.height()};
    };

class ToolbarStore {
    @observable currentParentSize = null;
    @observable isFitted = false;

    constructor(svg, parentContainer, nativeSize) {
        this.d3svg = d3.select(svg);
        this.$parentContainer = $(parentContainer);
        this.setParentSize();
        this.showResizeButton = _.isObject(nativeSize);
        this.nativeSize = nativeSize;
        this.isFitted = !_.isObject(nativeSize) || this.currentParentSize.width < nativeSize.width;
        this.scaleSize();
    }

    @action.bound setParentSize() {
        this.currentParentSize = getDomSize(this.$parentContainer);
    }

    @action.bound handleResizeClick() {
        this.isFitted = !this.isFitted;
        this.scaleSize();
    }

    @action.bound handlePageResize() {
        this.setParentSize();
        this.scaleSize();
    }

    @action.bound scaleSize() {
        if (this.isFitted) {
            // scale svg to parent container
            this.d3svg.attr("width", "100%").attr("height", "100%");
        } else {
            // scale svg to native size
            this.d3svg
                .attr(
                    "width",
                    this.currentParentSize.width > this.nativeSize.width
                        ? "100%"
                        : this.nativeSize.width
                )
                .attr("height", this.nativeSize.height);
        }
    }

    @computed get showZoom() {
        return (
            (this.isFitted && this.nativeSize.width > this.currentParentSize.width) ||
            (!this.isFitted && this.currentParentSize.width > this.nativeSize.width)
        );
    }
}

@observer
class VisualToolbar extends Component {
    constructor(props) {
        super(props);
        this.store = new ToolbarStore(props.svg, props.parentContainer, props.nativeSize);

        let resizeTimer;
        this.handleResizeEvent = () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(this.store.handlePageResize, 1000);
        };
    }

    componentDidMount() {
        window.addEventListener("resize", this.handleResizeEvent);
    }

    componentWillUnmount() {
        window.removeEventListener("resize", this.handleResizeEvent);
    }

    render() {
        const {showResizeButton, handleResizeClick} = this.store,
            {svg} = this.props;
        return (
            <div className="float-right">
                {showResizeButton ? (
                    <button className="btn btn-sm" title="Zoom in/out" onClick={handleResizeClick}>
                        <i
                            className={
                                this.store.showZoom ? "fa fa-search-plus" : "fa fa-search-minus"
                            }></i>
                    </button>
                ) : null}
                <div className="btn-group dropup" title="Download image">
                    <button className="btn btn-sm dropdown-toggle" data-toggle="dropdown">
                        <i className="fa fa-download"></i>
                    </button>
                    <div className="dropdown-menu float-right dropdown-menu-right">
                        <a
                            className="dropdown-item"
                            href="#"
                            onClick={() => downloadImage(svg, "svg")}>
                            <i className="fa fa-fw fa-picture-o"></i>&nbsp;Download SVG
                        </a>
                        <a
                            className="dropdown-item"
                            href="#"
                            onClick={() => downloadImage(svg, "pptx")}>
                            <i className="fa fa-fw fa-file-powerpoint-o"></i>&nbsp;Download PPTX
                        </a>
                        <a
                            className="dropdown-item"
                            href="#"
                            onClick={() => downloadImage(svg, "pdf")}>
                            <i className="fa fa-fw fa-file-pdf-o"></i>&nbsp;Download PDF
                        </a>
                        <a
                            className="dropdown-item"
                            href="#"
                            onClick={() => downloadImage(svg, "png")}>
                            <i className="fa fa-fw fa-picture-o"></i>&nbsp;Download PNG
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}

VisualToolbar.propTypes = {
    svg: PropTypes.object.isRequired,
    parentContainer: PropTypes.object.isRequired,
    nativeSize: PropTypes.shape({
        width: PropTypes.number.isRequired,
        height: PropTypes.number.isRequired,
    }),
};

export default VisualToolbar;
