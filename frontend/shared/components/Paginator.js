import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

const Paginator = props => {
    const {onChangePage, page} = props;

    if (page.total_pages === 1) {
        return null;
    }

    return (
        <ul className="pagination justify-content-center">
            {page.previous ? (
                <li className="page-item">
                    <button
                        className="page-link disabled"
                        onClick={() => onChangePage(page.previous)}>
                        &lt;&lt;
                    </button>
                </li>
            ) : null}
            <li className="page-item disabled">
                <span className="page-link">
                    {page.current_page} of {page.total_pages}
                </span>
            </li>
            {page.next ? (
                <li className="page-item">
                    <button className="page-link disabled" onClick={() => onChangePage(page.next)}>
                        &gt;&gt;
                    </button>
                </li>
            ) : null}
        </ul>
    );
};

Paginator.propTypes = {
    page: PropTypes.shape({
        current_page: PropTypes.number.isRequired,
        total_pages: PropTypes.number.isRequired,
        next: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        previous: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    }),
    onChangePage: PropTypes.func.isRequired,
};

export default observer(Paginator);
