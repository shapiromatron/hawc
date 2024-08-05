import {inject, observer} from "mobx-react";
import React, {Component} from "react";

import PrismaBoxesTable from "./PrismaBoxesTable";
import PrismaSectionsTable from "./PrismaSectionsTable";
import PrismaBulletedListsTable from "./PrismaBulletedListsTable";
import PrismaCardsTable from "./PrismaCardsTable";
import PrismaArrowsTable from "./PrismaArrowsTable";

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
