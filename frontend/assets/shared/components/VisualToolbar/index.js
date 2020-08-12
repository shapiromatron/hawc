import React, {Component} from "react";
import PropTypes from "prop-types";
import * as d3 from "d3";
import {action, observable} from "mobx";
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

    constructor(svg, parentContainer, nativeSize) {
        this.svg = svg;
        this.d3svg = d3.select(svg);
        this.$parentContainer = $(parentContainer);
        this.nativeSize = nativeSize;
        this.nativeAspectRatio = nativeSize.height / nativeSize.width;
        this.updateCurrentParentSize();
    }

    @action.bound updateCurrentParentSize() {
        this.currentParentSize = getDomSize($(this.parentContainer));
    }

    @action.bound isFullSize() {
        let currentSize = getDomSize(this.$parentContainer);
        return (
            currentSize.width >= this.nativeSize.width &&
            currentSize.height >= this.nativeSize.height
        );
    }
}

@observer
class VisualToolbar extends Component {
    constructor(props) {
        super(props);
        this.store = new ToolbarStore(props.svg, props.parentContainer, props.nativeSize);
    }
    componentDidMount() {
        const {
                $parentContainer,
                d3svg,
                nativeAspectRatio,
                isFullSize,
                updateCurrentParentSize,
            } = this.store,
            onPageResize = () => {
                const targetWidth = $parentContainer.width(),
                    targetHeight = targetWidth * nativeAspectRatio;

                $parentContainer.attr("width", targetWidth).attr("height", targetHeight);
                d3svg.attr("width", targetWidth).attr("height", targetHeight);
                if (!isFullSize()) {
                    updateCurrentParentSize();
                }
            };

        let resizeTimer;
        $(window).resize(() => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(onPageResize, 1000);
        });
    }
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
        const {$parentContainer, d3svg, nativeSize, currentParentSize, isFullSize} = this.store,
            makeFullSize = () => {
                $parentContainer
                    .attr("width", $parentContainer.width())
                    .attr("height", $parentContainer.height());
                d3svg.attr("width", nativeSize.width).attr("height", nativeSize.height);
            },
            setOriginalSize = () => {
                $parentContainer
                    .attr("width", currentParentSize.width)
                    .attr("height", currentParentSize.height);
                d3svg
                    .attr("width", currentParentSize.width)
                    .attr("height", currentParentSize.height);
            },
            handleClick = () => {
                if (isFullSize()) {
                    setOriginalSize();
                } else {
                    makeFullSize();
                }
            };
        return (
            <button className="btn btn-mini" title="Zoom in/out" onClick={handleClick}>
                <i className={isFullSize() ? "fa fa-search-minus" : "fa fa-search-plus"}></i>
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
    parentContainer: PropTypes.object.isRequired,
    nativeSize: PropTypes.shape({
        width: PropTypes.number.isRequired,
        height: PropTypes.number.isRequired,
    }).isRequired,
};

export default VisualToolbar;
