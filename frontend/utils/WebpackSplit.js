import React from "react";
import {render} from "react-dom";

const splitStartupRedux = function(element, Component, configureStore) {
    /*
        To use for code splitting:

        import { splitStartupRedux } from 'utils/WebpackSplit';

        const startup = function(element){
            System.import('path to Root container').then((Component) => {
                System.import('path to configureStore').then((store) => {
                    splitStartupRedux(element, Component.default, store.default);
                });
            });
        };

        export default startup;
    */
    const store = configureStore();
    render(<Component store={store} />, element);
};

const splitStartup = function(element, Component, data) {
    render(<Component data={data} />, element);
};

export {splitStartupRedux, splitStartup};
