import PropTypes from "prop-types";
import React, {Component} from "react";

import Reference from "./Reference";

class ReferenceTable extends Component {
    render() {
        const {references} = this.props,
            args = {showActions: this.props.showActions, showHr: true};

        if (references.length === 0) {
            return <p>No references found.</p>;
        }

        return (
            <div>
                {references.map((reference, i) => (
                    <Reference key={i} reference={reference} {...args} />
                ))}
            </div>
        );
    }
}
ReferenceTable.propTypes = {
    references: PropTypes.array.isRequired,
    showActions: PropTypes.bool.isRequired,
};

export default ReferenceTable;
