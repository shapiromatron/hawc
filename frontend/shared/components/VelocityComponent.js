import PropTypes from "prop-types";
import React, {Component} from "react";

class VelocityComponent extends Component {
    constructor(props) {
        super(props);
        this.state = {
            animated: false,
        };
        this.elementRef = React.createRef();
    }

    componentDidMount() {
        if (this.props.runOnMount) {
            // Use requestAnimationFrame to ensure the initial state is rendered before animation
            requestAnimationFrame(() => {
                this.setState({animated: true});
            });
        }
    }

    componentDidUpdate(prevProps) {
        // If runOnMount changes to true, start animation
        if (!prevProps.runOnMount && this.props.runOnMount) {
            this.setState({animated: true});
        }
    }

    render() {
        const {animation, duration, children} = this.props;
        const {animated} = this.state;

        // Apply animation styles when animated
        const animatedStyle = animated ? animation : {};

        // Create transition CSS for smooth animation
        const transitionDuration = `${duration}ms`;
        const transitionStyle = {
            transition: Object.keys(animation)
                .map(prop => `${prop} ${transitionDuration} ease-out`)
                .join(", "),
            ...animatedStyle,
        };

        // Clone the child element and apply the animation styles
        return React.cloneElement(React.Children.only(children), {
            ref: this.elementRef,
            style: {
                ...children.props.style,
                ...transitionStyle,
            },
        });
    }
}

VelocityComponent.propTypes = {
    animation: PropTypes.object.isRequired,
    duration: PropTypes.number,
    runOnMount: PropTypes.bool,
    children: PropTypes.element.isRequired,
};

VelocityComponent.defaultProps = {
    duration: 1000,
    runOnMount: false,
};

export default VelocityComponent;
