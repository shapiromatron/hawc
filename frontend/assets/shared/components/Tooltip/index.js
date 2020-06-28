import d3 from "d3";
import ReactDOM from "react-dom";
import React, {Component} from "react";
import PropTypes from "prop-types";

class TooltipContainer extends Component {
    render() {
        return (
            <div
                style={{
                    position: "absolute",
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

const bindTooltip = function($el, d3Selection, buildChildComponent, mouseEnterExtra) {
    /*

    Add tooltip to d3 selection. To use this method:

    - $el is a jQuery element where the tooltip is to be append
    - $d3Selection is a d3 selection of content
    - buildChildComponent builds the child
    */
    const xOffset = 10,
        yOffset = 10;

    $el.css("position", "absolute");

    d3Selection
        .on("mouseenter", function() {
            $el.css("display", "block");
            ReactDOM.render(
                <TooltipContainer>{buildChildComponent(...arguments)}</TooltipContainer>,
                $el[0]
            );
            if (mouseEnterExtra) {
                mouseEnterExtra();
            }
        })
        .on("mousemove", () =>
            $el.css({
                top: `${d3.event.pageY + xOffset}px`,
                left: `${d3.event.pageX + yOffset}px`,
            })
        )
        .on("mouseleave", () => $el.css("display", "none"));
};

export default bindTooltip;
