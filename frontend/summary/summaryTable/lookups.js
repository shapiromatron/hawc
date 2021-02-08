import GenericTableStore from "./genericTable/store.js";
import EvidenceProfileTableStore from "./evidenceProfileTable/store.js";
import {TableType} from "./constants";

import GenericTableForm from "./genericTable/TableForm";
import GenericTable from "./genericTable/Table";
import EvidenceProfileForm from "./evidenceProfileTable/Form";
import EvidenceProfileTable from "./evidenceProfileTable/Table";

const tableStoreLookup = {
        [TableType.GENERIC]: GenericTableStore,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTableStore,
    },
    tableViewComponentLookup = {
        [TableType.GENERIC]: GenericTable,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTable,
    },
    tableEditComponentLookup = {
        [TableType.GENERIC]: GenericTableForm,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileForm,
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
        const Component = tableViewComponentLookup[table.table_type];
        if (!Component) {
            throw `Unknown table type: ${table.table_type}`;
        }
        return Component;
    },
    getEditTableComponent = function(table) {
        const Component = tableEditComponentLookup[table.table_type];
        if (!Component) {
            throw `Unknown table type: ${table.table_type}`;
        }
        return Component;
    };

export {getTableStore, getViewTableComponent, getEditTableComponent};
