import React from "react";
import ReactDOM from "react-dom";

import DonutContainer from "./DonutContainer";

const robDonutStartup = data => {
    ReactDOM.render(<DonutContainer data={data} />, data.el);
};

export default robDonutStartup;
