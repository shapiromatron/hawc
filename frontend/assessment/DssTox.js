import React from "react";
import ReactDOM from "react-dom";

import DssToxDetailTable from "./components/DssToxDetailTable";

class DssTox {
    constructor(data) {
        this.data = data;
    }

    renderChemicalDetails(el, showHeader) {
        ReactDOM.render(<DssToxDetailTable object={this} showHeader={showHeader} />, el);
    }

    verbose_link() {
        // should be the same as hawc.apps.assessment.DSSTox.verbose_link
        return `<a href=${this.data.dashboard_url}>${this.data.dtxsid}</a>: ${this.data.content.preferredName} (CASRN ${this.data.content.casrn})`;
    }
}

export default DssTox;
