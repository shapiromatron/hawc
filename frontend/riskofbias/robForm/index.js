import React from "react";
import ReactDOM from "react-dom";

import store from "./store";
import Root from "./Root";

export default function(el) {
    ReactDOM.render(<Root store={store} />, el);
}
