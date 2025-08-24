import * as d3 from "d3";
import _ from "lodash";
import {action, makeObservable, observable} from "mobx";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import rasterize from "shared/utils/rasterize";

/*
Utility toolbelt for visualizations. Adds a few key attributes:

1) adds ability to download SVG
2) adds resizing button and triggering

*/
class ToolbarStore {
    @observable isFitted = false;

    constructor(svg, nativeSize) {
        makeObservable(this);
        this.d3svg = d3.select(svg);
        this.showResizeButton = _.isObject(nativeSize);
        this.nativeSize = nativeSize;
        this.isFitted = !_.isObject(nativeSize) || $($(svg).parent()[0]).width() < nativeSize.width;
        this.scaleSize();
    }

    @action.bound handleResizeClick() {
        this.isFitted = !this.isFitted;
        this.scaleSize();
    }

    @action.bound scaleSize() {
        if (this.isFitted) {
            // scale svg to parent container
            this.d3svg.attr("width", "100%").attr("height", "100%").style("min-width", null);
        } else {
            // scale svg to native size
            this.d3svg
                .attr("width", "100%")
                .attr("height", this.nativeSize.height)
                .style("min-width", this.nativeSize.width);
        }
    }
}

@observer
class VisualToolbar extends Component {
    constructor(props) {
        super(props);
        this.store = new ToolbarStore(props.svg, props.nativeSize);
    }

    render() {
        const {showResizeButton, handleResizeClick} = this.store,
            {svg} = this.props;
        return (
            <div className="float-right">
                {showResizeButton ? (
                    <button className="btn btn-sm" title="Zoom in/out" onClick={handleResizeClick}>
                        <i className={"fa fa-search-plus"}></i>
                    </button>
                ) : null}
                <div className="btn-group dropup" title="Download image">
                    <button className="btn btn-sm dropdown-toggle" data-toggle="dropdown">
                        <i className="fa fa-download"></i>
                    </button>
                    <div className="dropdown-menu float-right dropdown-menu-right">
                        <a className="dropdown-item" href="#" onClick={() => rasterize(svg, "svg")}>
                            <i className="fa fa-fw fa-file-code-o"></i>&nbsp;Download as a SVG
                        </a>
                        <a className="dropdown-item" href="#" onClick={() => rasterize(svg, "png")}>
                            <i className="fa fa-fw fa-picture-o"></i>&nbsp;Download as a PNG
                        </a>
                        <a
                            className="dropdown-item"
                            href="#"
                            onClick={() => rasterize(svg, "jpeg")}>
                            <i className="fa fa-fw fa-picture-o"></i>&nbsp;Download as a JPEG
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}

VisualToolbar.propTypes = {
    svg: PropTypes.object.isRequired,
    nativeSize: PropTypes.shape({
        width: PropTypes.number.isRequired,
        height: PropTypes.number.isRequired,
    }),
};

export default VisualToolbar;
