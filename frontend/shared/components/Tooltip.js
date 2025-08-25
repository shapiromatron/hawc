import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";
import h from "shared/utils/helpers";

class TooltipContainer extends Component {
    render() {
        return (
            <div
                style={{
                    backgroundColor: "white",
                    pointerEvents: "none",
                }}>
                {this.props.children}
            </div>
        );
    }
}
TooltipContainer.propTypes = {
    children: PropTypes.element.isRequired,
};

const bindTooltip = function ($el, d3Selection, buildChildComponent, options) {
    /*

    Add tooltip to d3 selection. To use this method:

    - $el is a jQuery element where the tooltip is to be append
    - $d3Selection is a d3 selection of content
    - buildChildComponent builds the child
    - mouseEnterExtra (optional) is any extra methods called on `mouseenter` event
    */
    const xOffset = 10,
        yOffset = 10,
        opts = options || {},
        parentOffsets = h.getAbsoluteOffsets($el[0].offsetParent);

    $el.css("position", "absolute");

    // unbind existing
    d3Selection.on("mouseenter", null).on("mousemove", null).on("mouseleave", null);

    // bind new
    d3Selection
        .on("mouseenter", function () {
            $el.css("display", "block");
            const root = createRoot($el[0]);
            root.render(<TooltipContainer>{buildChildComponent(...arguments)}</TooltipContainer>);
            if (opts.mouseEnterExtra) {
                opts.mouseEnterExtra(...arguments);
            }
        })
        .on("mousemove", event => {
            const box = $el[0].getBoundingClientRect(),
                {pageX, pageY} = event,
                relativeX = pageX - parentOffsets.left,
                relativeY = pageY - parentOffsets.top;

            $el.css({
                left: `${
                    pageX + xOffset + box.width < window.pageXOffset + window.innerWidth
                        ? relativeX + xOffset
                        : relativeX - xOffset - box.width
                }px`,
                top: `${
                    pageY + yOffset + box.height < window.pageYOffset + window.innerHeight
                        ? relativeY + yOffset
                        : relativeY - yOffset - box.height
                }px`,
            });
        })
        .on("mouseleave", () => $el.css("display", "none"));
};

export default bindTooltip;
