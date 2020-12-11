import $ from "$";
import React from "react";
import PropTypes from "prop-types";

class Modal extends React.Component {
    constructor(props) {
        super(props);
        this.domNode = React.createRef();
    }

    componentDidMount() {
        $(this.domNode.current).modal({show: false});
    }

    componentWillUnmount() {
        $(this.domNode.current).off("hidden", this.handleHidden);
    }

    show(cb) {
        const $modal = $(this.domNode.current);
        if (cb) {
            $modal.one("shown.bs.modal", cb);
        }
        $modal.modal("show");
    }

    hide() {
        $(this.domNode.current).modal("hide");
    }

    render() {
        return (
            <div
                ref={this.domNode}
                className="modal fade"
                tabIndex="-1"
                role="dialog"
                aria-hidden="true">
                {this.props.dialog}
            </div>
        );
    }
}

Modal.propTypes = {
    dialog: PropTypes.node.isRequired,
};

export default Modal;
