import PropTypes from "prop-types";
import React, {useEffect, useRef, useState} from "react";

function VelocityComponent({animation, duration, easing, runOnMount, children}) {
    const [animated, setAnimated] = useState(false);
    const elementRef = useRef();

    useEffect(() => {
        if (runOnMount) {
            // Use requestAnimationFrame to ensure the initial state is rendered before animation
            requestAnimationFrame(() => {
                setAnimated(true);
            });
        }
    }, [runOnMount]);

    // Apply animation styles when animated
    const animatedStyle = animated ? animation : {},
        transitionDuration = `${duration}ms`,
        transitionStyle = {
            transition: Object.keys(animation)
                .map(prop => `${prop} ${transitionDuration} ${easing}`)
                .join(", "),
            ...animatedStyle,
        };

    // Clone the child element and apply the animation styles
    // This preserves the original element's props and accessibility attributes
    return React.cloneElement(React.Children.only(children), {
        ref: elementRef,
        style: {
            ...children.props.style,
            ...transitionStyle,
        },
    });
}

VelocityComponent.propTypes = {
    animation: PropTypes.object.isRequired,
    duration: PropTypes.number,
    easing: PropTypes.string,
    runOnMount: PropTypes.bool,
    children: PropTypes.element.isRequired,
};

VelocityComponent.defaultProps = {
    duration: 1000,
    easing: "ease-out",
    runOnMount: false,
};

export default VelocityComponent;
