import {inject, observer} from "mobx-react";
import React, {Component} from "react";

import PrismaArrowsTable from "./PrismaArrowsTable";
import PrismaBoxesTable from "./PrismaBoxesTable";
import PrismaBulletedListsTable from "./PrismaBulletedListsTable";
import PrismaCardsTable from "./PrismaCardsTable";
import PrismaSectionsTable from "./PrismaSectionsTable";

@inject("store")
@observer
class PrismaDataTab extends Component {
    render() {
        return (
            <div>
                <PrismaSectionsTable />
                <PrismaBoxesTable />
                <PrismaBulletedListsTable />
                <PrismaCardsTable />
                <PrismaArrowsTable />
            </div>
        );
    }
}
export default PrismaDataTab;
