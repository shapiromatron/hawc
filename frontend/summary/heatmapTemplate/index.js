import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import HeatmapTemplateRoot from "./HeatmapTemplateRoot";
import HeatmapTemplateStore from "./HeatmapTemplateStore";

export default function (el, config) {
    const store = new HeatmapTemplateStore(config);

    createRoot(el).render(
        <Provider store={store}>
            <HeatmapTemplateRoot />
        </Provider>
    );
}
