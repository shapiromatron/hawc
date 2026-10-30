import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

@inject("store")
@observer
class OverallPanel extends Component {
    // Move an existing form not created by React in/out of this component.
    constructor(props) {
        super(props);
        this.divRef = React.createRef();
        this.form = document.getElementById("visualForm");
        this.formParent = this.form.parentNode;
    }
    componentDidMount() {
        if (this.form && this.divRef.current) {
            this.divRef.current.appendChild(this.form);
        }
    }
    componentWillUnmount() {
        this.formParent.appendChild(this.form);
    }
    render() {
        return <div ref={this.divRef}></div>;
    }
}

OverallPanel.propTypes = {
    store: PropTypes.object,
};

export default OverallPanel;
