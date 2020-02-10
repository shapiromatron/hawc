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
        if (a.data.year > b.data.year) return 1;
        if (a.data.year < b.data.year) return -1;
        return 0;
    }

    print_self(options) {
        options = options || {};
        let content = [],
            getTitle = () => {
                if (this.data.title) {
                    return `<p class="ref_title">${this.data.title}</p>`;
                }
            },
            getJournal = () => {
                let journal = this.data.journal ? `${this.data.journal}<br/>` : "";
                return `<p class="ref_small">${journal}</p>`;
            },
            getAbstract = () => {
                if (this.data.abstract) return `<p class="abstracts">${this.data.abstract}</p>`;
            },
            getAuthors = () => {
                let authors =
                        this.data.authors_list || this.data.authors || Reference.no_authors_text,
                    year = this.data.year || "",
                    p = $(`<p class="ref_small">${authors} ${year}</p>`);

                // return content or undefined
                if (options.showActions && window.canEdit) {
                    var ul = $('<ul class="dropdown-menu">')
                        .append(
                            `<li><a href="${this.data.editTagUrl}" target="_blank">Edit tags</a></li>`
                        )
                        .append(
                            `<li><a href="${this.data.editReferenceUrl}" target="_blank">Edit reference</a></li>`
                        );

                    $('<div class="btn-group pull-right">')
                        .append(
                            '<a class="btn btn-small dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>'
                        )
                        .append(ul)
                        .appendTo(p);
                }

                return p;
            },
            getSearches = () => {
                if (this.data.searches) {
                    let links = this.data.searches
                            .map(d => `<a href="${d.url}">${d.title}</a>`)
                            .join("<span>,&nbsp;</span>"),
                        text = `<p><strong>HAWC searches/imports:</strong> ${links}</p>`;

                    return $("<div>").append(text);
                }
            },
            getIdentifiers = () => {
                var links = $("<div>"),
                    addHawcId = () => {
                        let grp = $('<div class="btn-group">'),
                            link = `<a class="btn btn-mini btn-warning" target="_blank" href="${this.data.url}">HAWC</a>`,
                            copyID = $(
                                `<button type="button" class="btn btn-mini btn-warning" title="Copy to clipboard"><i class="fa fa-clipboard"></i></button>`
                            );

                        // copy ID to clipboard
                        new Clipboard(copyID.get(0), {text: () => this.data.pk});

                        links.append(grp.append(link, copyID), "<span>&nbsp;</span>");
                    };

                if (this.data.full_text_url) {
                    let grp = $('<div class="btn-group">'),
                        link = `<a class="btn btn-mini btn-primary" target="_blank" href="${this.data.full_text_url}">Full text link</a>`,
                        copyID = $(
                            `<button type="button" class="btn btn-mini btn-primary" title="Copy to clipboard"><i class="fa fa-clipboard"></i></button>`
                        );

                    // copy ID to clipboard
                    new Clipboard(copyID.get(0), {text: () => this.data.full_text_url});

                    links.append(grp.append(link, copyID), "<span>&nbsp;</span>");
                }

                _.chain(this.data.identifiers)
                    .filter(v => v.url.length > 0)
                    .sortBy(v => v.database_id)
                    .each(function(v) {
                        let grp = $('<div class="btn-group">'),
                            link = `<a class="btn btn-mini btn-success" target="_blank" href="${v.url}" title="View ${v.id}">${v.database}</a>`,
                            copyID = $(
                                `<button type="button" class="btn btn-mini btn-success" title="Copy to clipboard"><i class="fa fa-clipboard"></i></button>`
                            );

                        // copy ID to clipboard
                        new Clipboard(copyID.get(0), {text: () => v.id});

                        links.append(grp.append(link, copyID), "<span>&nbsp;</span>");
                    })
                    .value();

                links.append(addHawcId());

                _.chain(this.data.identifiers)
                    .reject(v => v.url.length > 0 || v.database === "External link")
                    .sortBy(v => v.database_id)
                    .each(function(v) {
                        let grp = $('<div class="btn-group">'),
                            link = `<button type="button" class="btn btn-mini">${v.database}</a>`,
                            copyID = $(
                                `<button type="button" class="btn btn-mini" title="Copy to clipboard"><i class="fa fa-clipboard"></i></button>`
                            );

                        // copy ID to clipboard
                        new Clipboard(copyID.get(0), {text: () => v.id});

                        links.append(grp.append(link, copyID), "<span>&nbsp;</span>");
                    })
                    .value();

                return links;
            };

        if (options.showDetailsHeader) {
            content.push("<h4>Reference details:</h4>");
        }
        content.push(getAuthors());
        content.push(getTitle());
        content.push(getJournal());
        if (options.showTaglist) {
            content = content.concat(this.print_taglist());
        }
        content.push(getAbstract());
        content.push(getSearches());
        content.push(getIdentifiers());

        if (options.showHr) {
            content.push("<hr/>");
        }

        return $("<div>").html(content);
    }

    print_taglist() {
        var title = window.canEdit ? "click to remove" : "",
            cls = window.canEdit ? "refTag refTagEditing" : "refTag";
        return this.data.tags.map(d =>
            $(`<span title="${title}" class="${cls}">${d.get_full_name()}</span>`).data("d", d)
        );
    }

    print_short_name() {
        let authors = this.data.authors || this.data.authors_list || Reference.no_authors_text,
            year = this.data.year || "";
        this.$list = $(`<p class="reference">${authors} ${year}</p>`).data("d", this);
        return this.$list;
    }

    select_name() {
        this.$list.addClass("selected");
    }

    deselect_name() {
        this.$list.removeClass("selected");
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
