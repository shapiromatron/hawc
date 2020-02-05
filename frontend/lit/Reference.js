import $ from "$";
import _ from "lodash";
import Clipboard from "clipboard";

import Observee from "utils/Observee";

class Reference extends Observee {
    constructor(data, tagtree) {
        super();
        var self = this,
            tag_ids = data.tags;
        this.data = data;
        this.data.tags = [];
        tag_ids.forEach(function(v) {
            self.add_tag(tagtree.dict[v]);
        });
    }

    static sortCompare(a, b) {
        if (a.data.authors > b.data.authors) return 1;
        if (a.data.authors < b.data.authors) return -1;
        return 0;
    }

    print_self(show_taglist) {
        var taglist = show_taglist || false,
            content = [
                "<h4>Reference details:</h4>",
                `<p class="ref_small">${this.data.journal}</p>`,
                `<p class="ref_title">${this.data.title}</p>`,
                `<p class="ref_small">${this.data.authors || Reference.no_authors_text}</p>`,
            ];
        if (taglist) {
            content = content.concat(this.print_taglist());
        }
        content.push(`<p>${this.data.abstract}</p>`);
        content.push(this.getLinks());
        return content;
    }

    print_taglist() {
        var title = window.isEdit ? "click to remove" : "",
            cls = window.isEdit ? "refTag refTagEditing" : "refTag";
        return this.data.tags.map(d =>
            $(`<span title="${title}" class="${cls}">${d.get_full_name()}</span>`).data("d", d)
        );
    }

    print_name() {
        this.$list = $(
            '<p class="reference">{0} {1}</p>'.printf(
                this.data.authors || Reference.no_authors_text,
                this.data.year || ""
            )
        ).data("d", this);
        return this.$list;
    }

    select_name() {
        this.$list.addClass("selected");
    }

    deselect_name() {
        this.$list.removeClass("selected");
    }

    getLinks() {
        var links = $("<p>");

        if (this.data.full_text_url) {
            links.append(
                $("<a>")
                    .attr("class", "btn btn-mini btn-primary")
                    .attr("target", "_blank")
                    .attr("href", this.data.full_text_url)
                    .text("Full text link ")
                    .append('<i class="fa fa-fw fa-file-pdf-o"></i>')
            );
            links.append("<span>&nbsp;</span>");
        }

        _.chain(this.data.identifiers)
            .filter(function(v) {
                return v.url.length > 0;
            })
            .sortBy(function(v) {
                return v.database_id;
            })
            .each(function(v) {
                let grp = $('<div class="btn-group">'),
                    link = `<a class="btn btn-mini btn-success" target="_blank" href="${v.url}" title="View ${v.id}">${v.database}</a>`,
                    copyID = $(
                        `<button type="button" class="btn btn-mini btn-success" title="Copy ID ${v.id} to clipboard"><i class="fa fa-clipboard"></i></button>`
                    );

                // copy ID to clipboard
                new Clipboard(copyID.get(0), {text: () => v.id});

                links.append(grp.append(link, copyID));
                links.append("<span>&nbsp;</span>");
            })
            .value();

        _.chain(this.data.identifiers)
            .reject(function(v) {
                return v.url.length > 0 || v.database === "External link";
            })
            .sortBy(function(v) {
                return v.database_id;
            })
            .each(function(v) {
                let copyID = $(
                    `<button class="btn btn-mini" title="Copy ID ${v.id} to clipboard">${v.database} <i class="fa fa-clipboard"></i></button>`
                );

                // copy ID to clipboard
                new Clipboard(copyID.get(0), {text: () => v.id});

                links.append(copyID);
                links.append("<span>&nbsp;</span>");
            })
            .value();

        return links.children().length > 0 ? links : null;
    }

    print_div_row() {
        var self = this,
            data = this.data,
            div = $("<div>"),
            abs_btn = this.get_abstract_button(div),
            edit_btn = this.get_edit_button(),
            get_title = function() {
                if (data.title) return '<p class="ref_title">{0}</p>'.printf(data.title);
            },
            get_journal = function() {
                let journal = data.journal ? `${data.journal}<br/>` : "";
                return `<p class="ref_small">${journal}HAWC ID: ${data.pk}</p>`;
            },
            get_abstract = function() {
                if (data.abstract)
                    return '<p class="abstracts" style="display: none">{0}</p>'.printf(
                        data.abstract
                    );
            },
            get_authors_row = function() {
                var p = $(
                    '<p class="ref_small">{0} {1}</p>'.printf(
                        data.authors || Reference.no_authors_text,
                        data.year || ""
                    )
                );

                if (abs_btn || edit_btn) {
                    var ul = $('<ul class="dropdown-menu">');

                    if (abs_btn) ul.append($("<li>").append(abs_btn));
                    if (edit_btn) ul.append($("<li>").append(edit_btn));

                    $('<div class="btn-group pull-right">')
                        .append(
                            '<a class="btn btn-small dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>'
                        )
                        .append(ul)
                        .appendTo(p);
                }

                return p;
            },
            get_searches = function() {
                if (data.searches) {
                    let links = data.searches
                            .map(d => `<a href="${d.url}">${d.title}</a>`)
                            .join("<span>,&nbsp;</span>"),
                        text = `<p><strong>HAWC searches/imports:</strong> ${links}</p>`;

                    return $("<div>").append(text);
                }
            },
            populate_div = function() {
                return [
                    "<hr>",
                    get_authors_row(),
                    get_title(),
                    get_journal(),
                    get_abstract(),
                    self.getLinks(),
                ];
            };

        return div.html(populate_div().concat(this.print_taglist())).append(get_searches());
    }

    get_abstract_button(div) {
        // get abstract button if abstract available, or return undefined
        if (this.data.abstract) {
            return $("<a>")
                .text("Show abstract")
                .attr("class", "abstractToggle")
                .on("click", function() {
                    var sel = $(this);
                    if (sel.text() === "Show abstract") {
                        div.find(".abstracts").show();
                        sel.text("Hide abstract");
                    } else {
                        div.find(".abstracts").hide();
                        sel.text("Show abstract");
                    }
                });
        }
    }

    get_edit_button() {
        // return content or undefined
        if (window.canEdit) {
            return $("<div>")
                .append(
                    '<li><a href="{0}" target="_blank">Edit tags</a></li>'.printf(
                        this.edit_tags_url()
                    )
                )
                .append(
                    '<li><a href="{0}" target="_blank">Edit reference</a></li>'.printf(
                        this.edit_reference_url()
                    )
                );
        }
    }

    add_tag(tag) {
        var tag_already_exists = false;
        this.data.tags.forEach(function(v) {
            if (tag === v) {
                tag_already_exists = true;
            }
        });
        if (tag_already_exists) return;
        this.data.tags.push(tag);
        tag.addObserver(this);
        this.notifyObservers();
    }

    edit_tags_url() {
        return "/lit/reference/{0}/tag/".printf(this.data.pk);
    }

    edit_reference_url() {
        return "/lit/reference/{0}/edit/".printf(this.data.pk);
    }

    remove_tag(tag) {
        this.data.tags.splice_object(tag);
        tag.removeObserver(this);
        this.notifyObservers();
    }

    remove_tags() {
        this.data.tags = [];
        this.notifyObservers();
    }

    save(success, failure) {
        var data = {
            pk: this.data.pk,
            tags: this.data.tags.map(function(v) {
                return v.data.pk;
            }),
        };
        $.post(".", data, function(v) {
            return v.status === "success" ? success() : failure();
        }).fail(failure);
    }

    update(status) {
        if (status.event == "tag removed") {
            this.remove_tag(status.object);
        }
    }
}

_.extend(Reference, {
    no_authors_text: "[No authors listed]",
});

export default Reference;
