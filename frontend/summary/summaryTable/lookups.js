import GenericTableStore from "./genericTable/store.js";
import EvidenceProfileTableStore from "./evidenceProfileTable/store.js";
import {TableType} from "./constants";
import GenericTable from "./genericTable/Table";
import EvidenceProfileTable from "./evidenceProfileTable/Table";

const tableStoreLookup = {
        [TableType.GENERIC]: GenericTableStore,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTableStore,
    },
    tableComponentLookup = {
        [TableType.GENERIC]: GenericTable,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTable,
    },
    getTableStore = function(table, editStore) {
        const Cls = tableStoreLookup[table.table_type];
        if (!Cls) {
            throw `Unknown table type: ${table.table_type}`;
        }
        if (editStore) {
            return new Cls(true, JSON.parse(table.content), editStore);
        } else {
            return new Cls(false, table.content);
        }
    },
    getViewTableComponent = function(table) {
        const Component = tableComponentLookup[table.table_type];
        if (!Component) {
            throw `Unknown table type: ${table.table_type}`;
        }
        return Component;
    };

export {getTableStore, getViewTableComponent};
