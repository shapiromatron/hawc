import React from "react";

const wrapRow = function(children, rowClassName = "row", childClassName = "col-md-3") {
    /* Create a row with equally sized columns from a list of components. */
    return (
        <div className={rowClassName}>
            {children.map((el, i) => {
                return (
                    <div key={i} className={childClassName}>
                        {el}
                    </div>
                );
            })}
        </div>
    );
};

export default wrapRow;
