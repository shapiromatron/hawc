import _ from "lodash";

export const ReferenceStorageKey = "sortReferencesBy",
    SortBy = {
        // {value, label, sort method}
        AUTH_ASC: [
            "AUTH_ASC",
            "author ↑",
            [d => d.data.authors_short, d => d.data.year],
            ["asc", "asc"],
        ],
        AUTH_DESC: [
            "AUTH_DESC",
            "author ↓",
            [d => d.data.authors_short, d => d.data.year],
            ["desc", "asc"],
        ],
        YEAR_ASC: [
            "YEAR_ASC",
            "year ↑",
            [d => d.data.year, d => d.data.authors_short],
            ["asc", "asc"],
        ],
        YEAR_DESC: [
            "YEAR_DESC",
            "year ↓",
            [d => d.data.year, d => d.data.authors_short],
            ["desc", "asc"],
        ],
    },
    sortReferences = function(refs, sortByKey) {
        const key =
            sortByKey || window.localStorage.getItem(ReferenceStorageKey) || SortBy.YEAR_DESC[0];
        return _.orderBy(refs, SortBy[key][2], SortBy[key][3]);
    };
