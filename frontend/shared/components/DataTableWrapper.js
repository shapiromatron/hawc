import $ from "jquery";
import PropTypes from "prop-types";
import React, {createRef, useEffect, useState} from "react";
import Loading from "shared/components/Loading";

const DataTableWrapper = ({children, className, data, columns}) => {
    const ref = createRef(),
        [loading, setLoading] = useState(true);
    $.DataTable = require("datatables.net");
    useEffect(() => {
        // only include data/columns if they were provided
        const table = $(ref.current.firstElementChild).DataTable({
            autoWidth: false,
            order: [],
            pageLength: 10,
            ...(data ? {data} : {}),
            ...(columns ? {columns} : {}),
        });
        setLoading(false);
        return () => table.destroy();
    });
    return (
        <>
            {loading ? <Loading /> : null}
            <div ref={ref}>{children ? children : <table className={className}></table>}</div>
        </>
    );
};

DataTableWrapper.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    data: PropTypes.array,
    columns: PropTypes.array,
};

export default DataTableWrapper;
