import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import ReferenceTreeBrowseStore from "./ReferenceTreeBrowseStore";
import ReferenceTreeBrowse from "./ReferenceTreeBrowse";

let startupReferenceList = function(el, config) {
    ReactDOM.render(
        <Provider store={new ReferenceTreeBrowseStore(config)}>
            <ReferenceTreeBrowse />
        </Provider>,
        el
    );
};

export default startupReferenceList;
