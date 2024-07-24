import {inject, observer} from "mobx-react";
import React, {Component} from "react";

import PrismaBoxesTable from "./PrismaBoxesTable";
import PrismaSectionsTable from "./PrismaSectionsTable";

@inject("store")
@observer
class PrismaDataTab extends Component {
    render() {
        return (
            <div>
                <PrismaSectionsTable />
                <PrismaBoxesTable />
            </div>
        );
    }
}
export default PrismaDataTab;
