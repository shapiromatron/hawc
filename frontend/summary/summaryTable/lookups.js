import GenericTableStore from "./genericTable/store.js";
import EvidenceProfileTableStore from "./evidenceProfileTable/store.js";
import StudyOutcomeTableStore from "./studyOutcomeTable/store.js";
import {TableType} from "./constants";

import GenericTableForm from "./genericTable/TableForm";
import GenericTable from "./genericTable/Table";
import EvidenceProfileForm from "./evidenceProfileTable/Form";
import EvidenceProfileTable from "./evidenceProfileTable/Table";
import StudyOutcomeTableForm from "./studyOutcomeTable/TableForm";
import StudyOutcomeTable from "./studyOutcomeTable/Table";

const tableStoreLookup = {
        [TableType.GENERIC]: GenericTableStore,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTableStore,
        [TableType.STUDY_OUTCOME_TABLE]: StudyOutcomeTableStore,
    },
    tableViewComponentLookup = {
        [TableType.GENERIC]: GenericTable,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTable,
        [TableType.STUDY_OUTCOME_TABLE]: StudyOutcomeTable,
    },
    tableEditComponentLookup = {
        [TableType.GENERIC]: GenericTableForm,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileForm,
        [TableType.STUDY_OUTCOME_TABLE]: StudyOutcomeTableForm,
    },
    getTableStore = function(table, editStore) {
        const Cls = tableStoreLookup[table.table_type];
        if (!Cls) {
            throw `Unknown table type: ${table.table_type}`;
        }
        if (editStore) {
            table.content = JSON.parse(table.content);
            return new Cls(true, table, editStore);
        } else {
            return new Cls(false, table);
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
