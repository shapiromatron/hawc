import {TableType} from "./constants";
import EvidenceProfileForm from "./evidenceProfileTable/Form";
import EvidenceProfileTable from "./evidenceProfileTable/Table";
import EvidenceProfileTableStore from "./evidenceProfileTable/store.js";
import GenericTable from "./genericTable/Table";
import GenericTableForm from "./genericTable/TableForm";
import GenericTableStore from "./genericTable/store.js";
import StudyEvaluationData from "./studyEvaluationTable/DataForm";
import StudyEvaluationTable from "./studyEvaluationTable/Table";
import StudyEvaluationTableForm from "./studyEvaluationTable/TableForm";
import StudyEvaluationTableStore from "./studyEvaluationTable/store.js";

const tableStoreLookup = {
        [TableType.GENERIC]: GenericTableStore,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTableStore,
        [TableType.STUDY_EVALUATION_TABLE]: StudyEvaluationTableStore,
    },
    tableViewComponentLookup = {
        [TableType.GENERIC]: GenericTable,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileTable,
        [TableType.STUDY_EVALUATION_TABLE]: StudyEvaluationTable,
    },
    tableEditComponentLookup = {
        [TableType.GENERIC]: GenericTableForm,
        [TableType.EVIDENCE_PROFILE]: EvidenceProfileForm,
        [TableType.STUDY_EVALUATION_TABLE]: StudyEvaluationTableForm,
    },
    tableDataComponentLookup = {
        [TableType.STUDY_EVALUATION_TABLE]: StudyEvaluationData,
    },
    getTableStore = function (table, editStore) {
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
    getViewTableComponent = function (table) {
        const Component = tableViewComponentLookup[table.table_type];
        if (!Component) {
            throw `Unknown table type: ${table.table_type}`;
        }
        return Component;
    },
    getEditTableComponent = function (table) {
        const Component = tableEditComponentLookup[table.table_type];
        if (!Component) {
            throw `Unknown table type: ${table.table_type}`;
        }
        return Component;
    },
    getTableDataComponent = function (table) {
        const Component = tableDataComponentLookup[table.table_type];
        return Component;
    };

export {getEditTableComponent, getTableDataComponent, getTableStore, getViewTableComponent};
