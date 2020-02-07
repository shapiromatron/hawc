import $ from "$";

import HAWCUtils from "utils/HAWCUtils";

import Reference from "./Reference";

class ReferencesViewer {
    constructor($div, options) {
        this.options = options;
        this.$div = $div;
        this.$table_div = $('<div id="references_detail_block">');
        this.$div.html([this._print_header(), this.$table_div]);
        this._set_loading_view();
    }

    set_references(refs) {
        this.refs = refs.sort(Reference.sortCompare);
        this._build_reference_table();
    }

    set_error() {
        this.$table_div.html("<p>An error has occurred</p>");
    }

    view_untagged_references(tagtree, assessment_id, search_id) {
        let url = `/lit/assessment/${assessment_id}/references/untagged/json/`;
        if (search_id) {
            url += `?search_id=${search_id}`;
        }

        $.get(url, results => {
            if (results.status == "success") {
                this.set_references(results.refs.map(datum => new Reference(datum, tagtree)));
            } else {
                this.set_error();
            }
        });
    }

    _print_header() {
        var h3 = $("<h3>"),
            $div = this.$div,
            actionLinks = this.options.actionLinks || [],
            txt = this.options.fixed_title || "References";

        if (this.options.tag) {
            txt = 'References tagged: <span class="refTag">{0}</span>'.printf(
                this.options.tag.get_full_name()
            );

            actionLinks.push({
                url: `${this.options.download_url}?tag_id=${this.options.tag.data.pk}`,
                text: "Download references",
            });

            actionLinks.push({
                url: `${this.options.download_url}?tag_id=${this.options.tag.data.pk}&fmt=tb`,
                text: "Download references (table-builder format)",
            });

            if (window.canEdit) {
                actionLinks.push({
                    url: `/lit/tag/${this.options.tag.data.pk}/tag/`,
                    text: "Edit references with this tag (but not descendants)",
                });
            }
        }

        h3.html(txt);

        if (actionLinks.length > 0) {
            actionLinks.push({
                url: "#",
                text: "Show all abstracts",
                cls: "show_abstracts",
            });
            h3.append(HAWCUtils.pageActionsButton(actionLinks)).on(
                "click",
                ".show_abstracts",
                function(e) {
                    e.preventDefault();
                    if (this.textContent === "Show all abstracts") {
                        $div.find(".abstracts").show();
                        this.textContent = "Hide all abstracts";
                        $div.find(".abstractToggle").text("Hide abstract");
                    } else {
                        $div.find(".abstracts").hide();
                        this.textContent = "Show all abstracts";
                        $div.find(".abstractToggle").text("Show abstract");
                    }
                }
            );
        }

        return h3;
    }

    _set_loading_view() {
        this.$table_div.html('<p>Loading: <img src="/static/img/loading.gif"></p>');
    }

    _build_reference_table() {
        let content =
            this.refs.length === 0
                ? "<p>No references found.</p>"
                : this.refs.map(d => d.print_div_row());

        this.$table_div.html(content);
    }
}

export default ReferencesViewer;
