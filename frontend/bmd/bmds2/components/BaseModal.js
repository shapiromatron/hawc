import React from "react";
import $ from "$";

class BaseModal extends React.Component {
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
