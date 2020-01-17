import $ from "$";

import Reference from "./Reference";
import ReferencesViewer from "./ReferencesViewer";
import TagTree from "./TagTree";

let startupSearchReference = function(assessment_id, tags, canEdit) {
    window.assessment_pk = assessment_id;
    window.tagtree = new TagTree(tags);
    window.canEdit = canEdit;

    let refviewer = new ReferencesViewer($("#references_detail_div"), {
            fixed_title: "Search Results",
        }),
        handleResults = function(results) {
            if (results.status === "success") {
                let refs = results.refs.map(d => new Reference(d, window.tagtree));
                refviewer.set_references(refs);
            } else {
                refviewer.set_error();
            }
        },
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
        $.post(".", data).done(handleResults);
        $("#resultsHolder").fadeIn();
        $("#searchFormHolder").fadeOut();
    });

    $("#search_again").click(function() {
        $("#resultsHolder").fadeOut();
        $("#searchFormHolder").fadeIn();
    });
};

export default startupSearchReference;
