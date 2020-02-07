import $ from "$";

import Reference from "./Reference";

class EditReferenceContainer {
    constructor(refs, tagtree, settings) {
        this.refs = refs.sort(Reference.sortCompare);
        this.tagtree = tagtree;
        this.tagtree.addObserver(this);
        this.settings = settings;
        this.$div_content = $(settings.content_div);
        // build containers and load first reference
        this._build_containers();
        this._get_next_ref();
        this.load_reference();
    }

    _build_containers() {
        this.$div_selected_tags = $('<div class="well well-small"></div>');
        this.$div_details = $("<div></div>");
        this.$div_error = $("<div></div>");
        this.saved_icon = $('<span class="btn litSavedIcon" style="display: none;">Saved!</span>');
        this.$editRef = $(
            '<a class="btn pull-right" target="_blank" href="#" title="Cleanup imported reference details">Edit</a>'
        );

        var self = this,
            save_txt = this.refs.length > 1 ? "Save and go to next untagged" : "Save tags",
            button_save_and_next = $('<button class="btn btn-primary"></button>')
                .text(save_txt)
                .click(function() {
                    self.save_and_next();
                }),
            button_reset_tags = $('<button class="btn">Remove all tags</button>').click(function() {
                if (self.loaded_ref) self.loaded_ref.remove_tags();
            }),
            div_buttons = $("<div></div>").append([
                "<h4>Tags for current reference</h4>",
                this.$div_selected_tags,
                button_save_and_next,
                button_reset_tags,
                this.saved_icon,
                this.$editRef,
            ]),
            header = $("<h4>Available Tags</h4>");

        this.$div_reflist = $('<div class="span3"></div>');
        this._populate_reflist();

        this.$div_ref = $('<div class="span6"></div>').html([
            div_buttons,
            this.$div_error,
            this.$div_details,
        ]);

        this.$tags_content = this.load_tags().on("hawc-tagClicked", function(e) {
            var tag = $(e.target).data("d");
            self.loaded_ref.add_tag(tag);
        });

        this.$div_tags = $('<div class="span3"></div>').html([header, this.$tags_content]);
        this.$div_content.html([this.$div_reflist, this.$div_ref, this.$div_tags]);

        this.$div_selected_tags.on("click", ".refTag", function() {
            self.loaded_ref.remove_tag($(this).data("d"));
        });

        this.$div_reflist.on("click", ".reference", function() {
            self.unload_reference();
            self.loaded_ref = $(this).data("d");
            self.load_reference();
        });
    }

    unload_reference() {
        if (this.loaded_ref) {
            this._update_referencelist();
            this.loaded_ref.removeObserver(this);
            this.loaded_ref.deselect_name();
            this.loaded_ref = undefined;
        }
    }

    load_reference() {
        if (this.loaded_ref) {
            this.loaded_ref.addObserver(this);
            this.loaded_ref.select_name();
            this.$div_details.html(this.loaded_ref.print_self());
            this.$editRef.attr("href", this.loaded_ref.edit_reference_url());
            this.clear_errors();
            this._build_tagslist();
        }
    }

    _get_next_ref() {
        //Get the next reference that's untagged, unless none are available, If
        // none are available, just get the next one
        if (this.refs_untagged.length > 0) {
            this.loaded_ref = this.refs_untagged[0];
            this.load_reference();
        } else if (this.refs.length === 1 && this.refs_tagged.length === 1) {
            // if we are editing a single reference, display
            this.loaded_ref = this.refs_tagged[0];
            this.load_reference();
        } else {
            this.set_references_complete();
        }
    }

    save_and_next() {
        var self = this,
            success = function() {
                self.saved_icon.fadeIn().fadeOut({
                    complete() {
                        self.unload_reference();
                        self._get_next_ref();
                    },
                });
            },
            failure = function() {
                var txt =
                        "An error occurred in saving; please wait a moment and retry. If the error persists please contact HAWC staff.",
                    div = $("<div>")
                        .attr("class", "alert alert-danger")
                        .text(txt);
                self.$div_error.html(div).prepend("<br>");
            };
        if (this.loaded_ref) this.loaded_ref.save(success, failure);
    }

    update(status) {
        if (status === "TagTree") {
            this.$tags_content.html(this.load_tags());
        } else {
            //reference update
            this.load_reference();
        }
    }

    _populate_reflist() {
        var $refs_tagged = $('<div class="accordion-inner"></div>'),
            $refs_untagged = $('<div class="accordion-inner"></div>'),
            tagged = this.refs.filter(function(v) {
                return v.data.tags.length > 0;
            }),
            untagged = this.refs.filter(function(v) {
                return v.data.tags.length === 0;
            });

        tagged.forEach(function(v) {
            $refs_tagged.append(v.print_name());
        });
        untagged.forEach(function(v) {
            $refs_untagged.append(v.print_name());
        });

        var taggedbody = $(
                '<div id="references_tagged" class="accordion-body collapse in"></div>'
            ).append($refs_tagged),
            taggedgroup = $('<div class="accordion-group"></div>')
                .append(
                    '<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#references_lists" href="#references_tagged">Tagged</a></div>'
                )
                .append(taggedbody);

        var untaggedbody = $(
                '<div id="references_untagged" class="accordion-body collapse in"></div>'
            ).append($refs_untagged),
            untaggedgroup = $('<div class="accordion-group"></div>')
                .append(
                    '<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#references_lists" href="#references_untagged">Untagged</a></div>'
                )
                .append(untaggedbody);

        var acc = $('<div class="accordion" id="references_lists"></div>')
            .append(taggedgroup)
            .append(untaggedgroup);

        this.refs_tagged = tagged;
        this.refs_untagged = untagged;
        this.$refs_tagged = $refs_tagged;
        this.$refs_untagged = $refs_untagged;
        this.$div_reflist.html(["<h4>References</h4>", acc]);
    }

    _update_referencelist() {
        var self = this,
            has_tags = this.loaded_ref.data.tags.length > 0;
        if (has_tags) {
            var in_untagged = false;
            this.refs_untagged.forEach(function(v, i) {
                if (v === self.loaded_ref) {
                    self.refs_untagged.splice(i, 1);
                    in_untagged = true;
                }
            });
            if (in_untagged) {
                this.refs_tagged.push(this.loaded_ref);
                this.loaded_ref.$list.detach();
                this.$refs_tagged.append(this.loaded_ref.$list);
            }
        } else {
            var in_tagged = false;
            this.refs_tagged.forEach(function(v, i) {
                if (v === self.loaded_ref) {
                    self.refs_tagged.splice(i, 1);
                    in_tagged = true;
                }
            });
            if (in_tagged) {
                this.refs_untagged.push(this.loaded_ref);
                this.loaded_ref.$list.detach();
                this.$refs_untagged.append(this.loaded_ref.$list);
            }
        }
    }

    _build_tagslist() {
        this.$div_selected_tags.html(this.loaded_ref.print_taglist());
    }

    load_tags() {
        return this.tagtree.get_nested_list();
    }

    clear_errors() {
        this.$div_error.empty();
    }

    set_references_complete() {
        var txt = "All references have been successfully tagged. Congratulations!",
            div = $("<div>")
                .attr("class", "alert alert-success")
                .text(txt);
        this.$div_details.html(div).prepend("<br>");

        this.$div_selected_tags.html("");
    }
}

export default EditReferenceContainer;
