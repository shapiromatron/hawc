import $ from "jquery";
import PropTypes from "prop-types";
import React, {createRef, useEffect, useState} from "react";
import Loading from "shared/components/Loading";

const DataTableWrapper = ({children, className, data, columns}) => {
    const ref = createRef(),
        [loading, setLoading] = useState(true),
        dtProps = {autoWidth: false, order: [], pageLength: 10};

    // check that either children or data exist
    if (children) {
        // do nothing
    } else if (data && columns) {
        dtProps.data = data;
        dtProps.columns = columns;
    } else {
        console.error("Invalid props passed to DataTableWrapper");
    }

    $.DataTable = require("datatables.net");
    useEffect(() => {
        const table = $(ref.current.firstElementChild).DataTable(dtProps);
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
