import React from "react";

import $ from "$";

class BaseModal extends React.Component {
    /*
     * Temporary solution to modal issue. Closes modal when user presses escape,
     * however componentWillUnmount is not called so not ideal; should refactor
     * when we build a React-based modal.
     *
     * Requires this button to be in the component, triggers the boostrap close
     * event:
     *
     *      <button
     *          ref={this.closer}
     *          className="close"
     *          type="button"
     *          data-dismiss="modal">
     *          ×
     *      </button>
     *
     */

    constructor(props) {
        super(props);
        this.closer = React.createRef();
    }

    componentDidMount() {
        document.addEventListener("keydown", this.handleEscPress, false);
    }

    componentWillUnmount() {
        document.removeEventListener("keydown", this.handleEscPress, false);
    }

    handleEscPress = e => {
        if (e.keyCode === 27) {
            $(this.closer.current).click();
        }
    };
}

export default BaseModal;
