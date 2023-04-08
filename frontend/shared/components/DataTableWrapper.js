import $ from "jquery";
import PropTypes from "prop-types";
import React, {createRef, useEffect} from "react";

const DataTableWrapper = ({children}) => {
    const ref = createRef();
    $.DataTable = require("datatables.net");
    useEffect(() => {
        const table = $(ref.current.firstElementChild).DataTable({order: [], pageLength: 10});
        return () => table.destroy();
    });
    return <div ref={ref}>{children}</div>;
};

DataTableWrapper.propTypes = {
    children: PropTypes.node,
};

export default DataTableWrapper;
