import $ from "$";

import MetaProtocol from "./MetaProtocol";
import MetaResult from "./MetaResult";
import MetaResultListTable from "./MetaResultListTable";

export default {
    MetaProtocol,
    MetaResult,
    MetaResultListTable,
    startupMetaProtocolPage: (el, config) => MetaProtocol.displayFullPager($(el), config.id),
    startupMetaResultPage: (el, config) => MetaResult.displayFullPager($(el), config.id),
    startupMetaResultListPage: (el, config) => {
        const tbl = new MetaResultListTable(config.items);
        $(el).html(tbl.buildTable());
    },
};
