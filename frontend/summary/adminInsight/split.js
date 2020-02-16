import React from "react";
import ReactDOM from "react-dom";

import store from "./store";
import Root from "./Root";

let func = function(el) {
    ReactDOM.render(<Root store={store} />, el);
};

export default {
    func,
};
