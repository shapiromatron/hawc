import React from "react";
import {createRoot} from "react-dom/client";

import DonutContainer from "./DonutContainer";

const robDonutStartup = data => {
    createRoot(data.el).render(<DonutContainer data={data} />);
};

export default robDonutStartup;
