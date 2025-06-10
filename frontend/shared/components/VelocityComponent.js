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
    const animatedStyle = animated ? animation : {};

    // Create transition CSS for smooth animation
    const transitionDuration = `${duration}ms`,
        transitionStyle = {
            transition: Object.keys(animation)
                .map(prop => `${prop} ${transitionDuration} ${easing}`)
                .join(", "),
            ...animatedStyle,
        };

    // Use a wrapper div instead of cloning the child element for better accessibility
    return (
        <div ref={elementRef} style={transitionStyle}>
            {children}
        </div>
    );
}

VelocityComponent.propTypes = {
    animation: PropTypes.object.isRequired,
    duration: PropTypes.number,
    easing: PropTypes.string,
    runOnMount: PropTypes.bool,
    children: PropTypes.node.isRequired,
};

VelocityComponent.defaultProps = {
    duration: 1000,
    easing: "ease-out",
    runOnMount: false,
};

export default VelocityComponent;
