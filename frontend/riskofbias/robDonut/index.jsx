import React from "react";
import {createRoot} from "react-dom/client";

import DonutContainer from "./DonutContainer";

const robDonutStartup = data => {
    const root = createRoot(data.el);
    root.render(<DonutContainer data={data} />);
};

export default robDonutStartup;
