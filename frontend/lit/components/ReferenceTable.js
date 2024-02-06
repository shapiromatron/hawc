import PropTypes from "prop-types";
import React, {Component} from "react";
import Paginator from "shared/components/Paginator";

import Reference from "./Reference";

class ReferenceTable extends Component {
    render() {
        const {references, page, fetchPage} = this.props,
            args = {showActions: this.props.showActions, showHr: true};

        if (references.length === 0) {
            return <p>No references found.</p>;
        }

        return (
            <>
                <div>
                    {references.map((reference, i) => (
                        <Reference key={i} reference={reference} {...args} />
                    ))}
                </div>
                {page ? <Paginator page={page} onChangePage={fetchPage} /> : null}
            </>
        );
    }
}
ReferenceTable.propTypes = {
    references: PropTypes.array.isRequired,
    showActions: PropTypes.bool.isRequired,
    page: PropTypes.object,
    fetchPage: PropTypes.func,
};

export default ReferenceTable;
