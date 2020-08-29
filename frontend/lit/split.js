import $ from "$";
import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Reference from "./Reference";
import ReferenceComponent from "./components/Reference";
import ReferenceTreeMain from "./ReferenceTreeBrowse/Main";
import ReferenceTreeMainStore from "./ReferenceTreeBrowse/store";
import TagReferencesMain from "./TagReferences/Main";
import TagReferencesMainStore from "./TagReferences/store";
import ReferencesViewer from "./ReferencesViewer";
import TagTree from "./TagTree";
import TagTreeViz from "./TagTreeViz";

export default {
    Reference,
    ReferencesViewer,
    TagTree,
    TagTreeViz,
    startupReferenceDetail(el, tags, reference) {
        let tagtree = new TagTree(tags[0]),
            ref = new Reference(reference, tagtree),
            options = {showActions: true, actionsBtnClassName: "btn btn-primary dropdown-toggle"};

        ReactDOM.render(<ReferenceComponent reference={ref} {...options} />, el);
    },
    startupSearchReference(tags) {
        let tagtree = new TagTree(tags[0]),
            refviewer = new ReferencesViewer($("#references_detail_div"), {
                fixed_title: "Search Results",
            }),
            renderSearchRow = function(txt, label) {
                return txt ? `<p><b>${label}:</b>&nbsp;${txt}</p>` : "";
            },
            print_search_fields = function() {
                $("#search_context").html(`<div>
                ${renderSearchRow($("#id_id").val(), "HAWC ID")}
                ${renderSearchRow($("#id_title").val(), "Title")}
                ${renderSearchRow($("#id_authors").val(), "Authors")}
                ${renderSearchRow($("#id_journal").val(), "Journal/year")}
                ${renderSearchRow($("#id_db_id").val(), "Database ID")}
                ${renderSearchRow($("#id_abstract").val(), "Abstract")}
            </div>`);
            };

        $("#searchFormHolder > form").submit(function(event) {
            event.preventDefault();
            print_search_fields();
            let data = $(this).serialize();
            $.post(".", data).done(results => {
                if (results.status === "success") {
                    let refs = results.refs.map(d => new Reference(d, tagtree));
                    refviewer.set_references(refs);
                } else {
                    refviewer.set_error();
                }
            });
            $("#resultsHolder").fadeIn();
            $("#searchFormHolder").fadeOut();
        });

        $("#search_again").click(function() {
            $("#resultsHolder").fadeOut();
            $("#searchFormHolder").fadeIn();
        });
    },
    startupReferenceList(el, config) {
        ReactDOM.render(
            <Provider store={new ReferenceTreeMainStore(config)}>
                <ReferenceTreeMain />
            </Provider>,
            el
        );
    },
    startupTagReferences(el, config) {
        ReactDOM.render(
            <Provider store={new TagReferencesMainStore(config)}>
                <TagReferencesMain />
            </Provider>,
            el
        );
    },
};
