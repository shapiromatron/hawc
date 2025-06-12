import PropTypes from "prop-types";
import React from "react";
import $ from "$";

class Modal extends React.Component {
    constructor(props) {
        super(props);
        this.domNode = React.createRef();
    }

    componentDidMount() {
        $(this.domNode.current).modal({show: false});
        this.handleShownState();
    }

    componentWillUnmount() {
        $(this.domNode.current).off("hidden", this.handleHidden);
    }

    componentDidUpdate() {
        this.handleShownState();
    }

    handleShownState() {
        if (this.props.isShown) {
            this.show();
        } else {
            this.hide();
        }
    }

    show() {
        const $modal = $(this.domNode.current),
            {onClosed, onShown} = this.props;

        if (onShown) {
            $modal.one("shown.bs.modal", onShown);
        }
        if (this.props.onClosed) {
            $modal.one("hide.bs.modal", onClosed);
        }
        $modal.modal("show");
    }

    hide() {
        $(this.domNode.current).modal("hide");
    }

    render() {
        const {isShown, children} = this.props;
        return (
            <div
                ref={this.domNode}
                className={`modal fade showModal${isShown}`}
                tabIndex="-1"
                role="dialog"
                aria-hidden="true">
                <div className="modal-dialog" role="document">
                    <div className="modal-content">{children}</div>
                </div>
            </div>
        );
    }
}

Modal.propTypes = {
    children: PropTypes.node.isRequired,
    isShown: PropTypes.bool.isRequired,
    onShown: PropTypes.func,
    onClosed: PropTypes.func,
};

export default Modal;
