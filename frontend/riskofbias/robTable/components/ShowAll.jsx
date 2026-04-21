import PropTypes from "prop-types";
import React, {Component} from "react";

class ShowAll extends Component {
    render() {
        const {handleClick, allShown} = this.props;
        return (
            <button className="btn btn-sm" onClick={handleClick}>
                <i className={allShown ? "fa fa-minus fa-fw" : "fa fa-plus fa-fw"} />
                {allShown ? "Hide all details" : "Show all details"}
            </button>
        );
    }
}

ShowAll.propTypes = {
    allShown: PropTypes.bool.isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ShowAll;
