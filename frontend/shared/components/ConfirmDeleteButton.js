import PropTypes from "prop-types";
import React from "react";

class ConfirmDeleteButton extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            deleteInitiated: false,
        };
    }
    render() {
        const {handleDelete, deleteText} = this.props,
            {deleteInitiated} = this.state,
            handleClick = e => {
                if (deleteInitiated) {
                    handleDelete(e);
                } else {
                    this.setState({deleteInitiated: true});
                }
            },
            buttonClass = deleteInitiated ? "btn btn-outline-danger" : "btn btn-danger",
            buttonText = deleteInitiated ? "Click again to confirm" : deleteText;

        return (
            <button className={buttonClass} onClick={handleClick}>
                <i className="fa fa-trash mr-1"></i>
                {buttonText}
            </button>
        );
    }
}

ConfirmDeleteButton.propTypes = {
    handleDelete: PropTypes.func.isRequired,
    deleteText: PropTypes.string,
};

ConfirmDeleteButton.defaultProps = {
    deleteText: "Delete",
};

export default ConfirmDeleteButton;
