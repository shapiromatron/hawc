import { inject, observer, observer } from "mobx-react";
import PropTypes from "prop-types";
import React, { Component } from "react";

@inject("store")
@observer
class PrismaDataTab extends Component {
    render() {
        <div>
            <PrismaSectionsTable/>
        </div>
    }
}
;
export default PrismaDataTab;
