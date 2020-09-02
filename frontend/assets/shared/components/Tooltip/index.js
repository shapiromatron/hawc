import * as d3 from "d3";
import ReactDOM from "react-dom";
import React, {Component} from "react";
import PropTypes from "prop-types";

class TooltipContainer extends Component {
    render() {
        return (
            <div
                style={{
                    backgroundColor: "white",
                }}>
                {this.props.children}
            </div>
        );
    }
}
TooltipContainer.propTypes = {
    children: PropTypes.element.isRequired,
};

const bindTooltip = function($el, d3Selection, buildChildComponent, options) {
    /*

    Add tooltip to d3 selection. To use this method:

    - $el is a jQuery element where the tooltip is to be append
    - $d3Selection is a d3 selection of content
    - buildChildComponent builds the child
    - mouseEnterExtra (optional) is any extra methods called on `mouseenter` event
    */
    const xOffset = 10,
        yOffset = 10,
        opts = options || {};

    $el.css("position", "absolute");

    // unbind existing
    d3Selection
        .on("mouseenter", null)
        .on("mousemove", null)
        .on("mouseleave", null);

    // bind new
    d3Selection
        .on("mouseenter", function() {
            $el.css("display", "block");
            ReactDOM.render(
                <TooltipContainer>{buildChildComponent(...arguments)}</TooltipContainer>,
                $el[0]
            );
            if (opts.mouseEnterExtra) {
                opts.mouseEnterExtra(...arguments);
            }
        })
        .on("mousemove", () => {
            const box = $el[0].getBoundingClientRect(),
                {pageX, pageY} = d3.event;
            $el.css({
                left: `${
                    pageX + xOffset + box.width < window.pageXOffset + window.innerWidth
                        ? pageX + xOffset
                        : pageX - xOffset - box.width
                }px`,
                top: `${
                    pageY + yOffset + box.height * 0.5 < window.pageYOffset + window.innerHeight
                        ? pageY + yOffset - box.height * 0.5
                        : window.pageYOffset + window.innerHeight - yOffset - box.height
                }px`,
            });
        })
        .on("mouseleave", () => $el.css("display", "none"));
};

export default bindTooltip;
