import PropTypes from "prop-types";
import React, {useEffect, useRef, useState} from "react";

function Animation({
    animation,
    duration = 1000,
    easing = "ease-out",
    runAnimation = true,
    children,
}) {
    const [animated, setAnimated] = useState(false),
        elementRef = useRef();

    useEffect(() => {
        // ensure initial state is rendered before animation
        if (runAnimation) {
            requestAnimationFrame(() => setAnimated(true));
        }
    }, [runAnimation]);

    // Apply animation styles when animated
    const animatedStyle = animated ? animation : {},
        transitionDuration = `${duration}ms`,
        transitionStyle = {
            transition: Object.keys(animation)
                .map(prop => `${prop} ${transitionDuration} ${easing}`)
                .join(", "),
            ...animatedStyle,
        };

    // Clone child element and apply animation styles; this preserves the original
    // element's props and accessibility attributes.
    return React.cloneElement(React.Children.only(children), {
        ref: elementRef,
        style: {...children.props.style, ...transitionStyle},
    });
}

Animation.propTypes = {
    animation: PropTypes.object.isRequired,
    duration: PropTypes.number,
    easing: PropTypes.string,
    runAnimation: PropTypes.bool,
    children: PropTypes.element.isRequired,
};

export default Animation;
