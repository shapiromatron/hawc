var Reference = function(data, tagtree){
    Observee.apply(this, arguments);
    var self = this,
        tag_ids = data.tags;
    this.data = data;
    this.data.tags = [];
    tag_ids.forEach(function(v){self.add_tag(tagtree.dict[v]);});
};
_.extend(Reference, {
    no_authors_text: "[No authors listed]",
    sortCompare: function(a,b){
      if (a.data.authors > b.data.authors) return 1;
      if (a.data.authors < b.data.authors) return -1;
      return 0;
    }
});
_.extend(Reference.prototype, Observee.prototype, {
    print_self: function(show_taglist){
        var taglist = show_taglist || false,
            content = [
                '<h4>Reference details:</h4>',
                '<p class="ref_small">{0}</p>'.printf(this.data.journal),
                '<p class="ref_title">{0}</p>'.printf(this.data.title),
                '<p class="ref_small">{0}</p>'.printf(this.data.authors || Reference.no_authors_text)
            ];
        if(taglist){
            content = content.concat(this.print_taglist());
        }
        content.push('<p>{0}</p>'.printf(this.data.abstract));
        content.push(this.getLinks());
        return content;
    },
    print_taglist: function(){
        var title = (window.isEdit) ? "click to remove" : "",
            cls = (window.isEdit) ? "refTag refTagEditing" : "refTag";
        return _.map(this.data.tags, function(d){
            return $('<span title="{0}" class="{1}">{2}</span>'
                        .printf(title, cls, d.get_full_name())).data('d', d);
        });
    },
    print_name: function(){
        this.$list = $('<p class="reference">{0} {1}</p>'.printf(
            this.data.authors || Reference.no_authors_text, this.data.year || ""))
            .data('d', this);
        return this.$list;
    },
    select_name: function(){
        this.$list.addClass("selected");
    },
    deselect_name: function(){
        this.$list.removeClass("selected");
    },
    getLinks: function(){
        var links = $('<p>');

        _.chain(this.data.identifiers)
            .filter(function(v){return v.url.length>0;})
            .each(function(v){
                links.append('<a class="btn btn-mini btn-success" target="_blank" href="{0}">{1} ID {2}</a>'.printf(
                    v.url, v.database, v.id));
                links.append('<span>&nbsp;</span>');
            });

        if (this.data.full_text_url){
            links.append($('<a>')
                .attr("class", 'btn btn-mini btn-success')
                .attr('target', '_blank')
                .attr('href', this.data.full_text_url)
                .text("Full text link"));
        }

        return (links.children().length>0) ? links : null;
    },
    print_div_row: function(){

        var self = this,
            data = this.data,
            div = $('<div>'),
            abs_btn = this.get_abstract_button(div),
            edit_btn = this.get_edit_button(),
            get_title = function(){
                if(data.title)
                    return '<p class="ref_title">{0}</p>'.printf(data.title);
            },
            get_journal = function(){
                if(data.journal)
                    return '<p class="ref_small">{0}</p>'.printf(data.journal);
            },
            get_abstract = function(){
                if(data.abstract)
                    return '<p class="abstracts collapse">{0}</p>'.printf(data.abstract);
            },
            get_authors_row = function(){
                var p = $('<p class="ref_small">{0} {1}</p>'.printf(
                            data.authors || Reference.no_authors_text,
                            data.year || ""));

                if(abs_btn || edit_btn){
                    var ul = $('<ul class="dropdown-menu">');

                    if (abs_btn) ul.append($('<li>').append(abs_btn));
                    if (edit_btn) ul.append($('<li>').append(edit_btn));

                    $('<div class="btn-group pull-right">')
                        .append('<a class="btn btn-small dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>')
                        .append(ul)
                        .appendTo(p);
                }

                return p;
            },
            get_searches = function(){
                if(data.searches){
                    var title = "<p><strong>HAWC searches/imports:</strong></p>",
                        ul = $('<ul>').html(_.map(data.searches, function(d){return '<li><a href="{0}">{1}</a></li>'.printf(d.url, d.title);}));
                    return $('<div>').append(title, ul);
                }
            },
            populate_div = function(){
                return [
                    '<hr>',
                    get_authors_row(),
                    get_title(),
                    get_journal(),
                    get_abstract(),
                    self.getLinks(),
                ];
            };

        return div.html(populate_div().concat(this.print_taglist())).append(get_searches());
    },
    get_abstract_button: function(div){
        // get abstract button if abstract available, or return undefined
        if(this.data.abstract){
            return $('<a>')
                .text("Show abstract")
                .attr("class", "abstractToggle")
                .on('click', function(){
                    var sel = $(this);
                    if(sel.text() === "Show abstract"){
                        div.find('.abstracts').collapse('show');
                        sel.text("Hide abstract");
                    } else {
                        div.find('.abstracts').collapse('hide');
                        sel.text("Show abstract");
                    }
                });
        };
    },
    get_edit_button: function(){
        // get edit button if editing enabled, or return undefined
        if(window.canEdit){
            return $('<a>')
                .text('Edit tags')
                .attr('href', this.edit_tags_url())
                .attr('target', '_blank');
        }
    },
    add_tag: function(tag){
        var tag_already_exists = false;
        this.data.tags.forEach(function(v){if(tag===v){tag_already_exists=true;}});
        if(tag_already_exists) return;
        this.data.tags.push(tag);
        tag.addObserver(this);
        this.notifyObservers();
    },
    edit_tags_url: function(){
        return "/lit/reference/{0}/tag/".printf(this.data.pk);
    },
    remove_tag: function(tag){
        this.data.tags.splice_object(tag);
        tag.removeObserver(this);
        this.notifyObservers();
    },
    remove_tags: function(){
        this.data.tags = [];
        this.notifyObservers();
    },
    save: function(success, failure){
        var data = {"pk": this.data.pk,
                    "tags": this.data.tags.map(function(v){return v.data.pk;})};
        $.post('.', data, function(v) {
            return (v.status==="success") ? success() : failure();
        }).fail(failure);
    },
    update: function(status){
        if (status.event =="tag removed"){this.remove_tag(status.object);}
    }
});


var ReferencesViewer = function($div, options){
    this.options = options;
    this.$div = $div;

    this.$table_div = $('<div id="references_detail_block"></div>');
    this.$div.html([this._print_header(), this.$table_div]);
    this._set_loading_view();
};
ReferencesViewer.prototype = {
    set_references: function(refs){
        this.refs = refs.sort(Reference.sortCompare);
        this._build_reference_table();
    },
    set_error: function(){
        this.$table_div.html('<p>An error has occured</p>');
    },
    _print_header: function(){
        var h3 = $('<h3>')
            $div = this.$div,
            actionLinks = this.options.actionLinks || [],
            txt = this.options.fixed_title || "References";

        if(this.options.tag){
            txt = "References tagged: <span class='refTag'>{0}</span>".printf(this.options.tag.get_full_name());

            actionLinks.push({
                url: "{0}?tag_id={1}".printf(this.options.download_url, this.options.tag.data.pk),
                text: "Download references"
            });

            if (window.canEdit){
                actionLinks.push({
                    url: "/lit/tag/{0}/tag/".printf(this.options.tag.data.pk),
                    text: "Edit references with this tag (but not descendants)"
                });
            }
        }

        h3.html(txt);

        if(actionLinks.length>0)
            actionLinks.push({
                url: "#",
                text: "Show all abstracts",
                cls: "show_abstracts"
            });
            h3.append(HAWCUtils.pageActionsButton(actionLinks))
                .on('click', '.show_abstracts', function(e){
                    e.preventDefault();
                    if(this.textContent === "Show all abstracts"){
                        $div.find('.abstracts').collapse('show');
                        this.textContent = "Hide all abstracts";
                        $div.find('.abstractToggle').text('Hide abstract');
                    } else {
                        $div.find('.abstracts').collapse('hide');
                        this.textContent = "Show all abstracts";
                        $div.find('.abstractToggle').text('Show abstract');
                    }
                });

        return h3;
    },
    _set_loading_view: function(){
        this.$table_div.html('<p>Loading: <img src="/static/img/loading.gif"/></p>');
    },
    _build_reference_table: function(){
        var content
        if(this.refs.length===0){
            content = "<p>No references found.</p>";
        } else {
            content = _.map(this.refs, function(d){ return d.print_div_row()});
        }
        this.$table_div.html(content);
    }
};


var EditReferenceContainer = function(refs, tagtree, settings){
    this.refs = refs.sort(Reference.sortCompare);
    this.tagtree = tagtree;
    this.tagtree.addObserver(this);
    this.$div_content = $(settings.content_div);
    // build containers and load first reference
    this._build_containers();
    this._get_next_ref();
    this.load_reference();
};
EditReferenceContainer.prototype = {
    _build_containers: function(){

        this.$div_selected_tags = $("<div class='well well-small'></div>");
        this.$div_details = $('<div></div>');
        this.$div_error = $('<div></div>');
        this.saved_icon = $('<span class="btn litSavedIcon" style="display: none;">Saved!</span>');

        var self = this,
            save_txt = (this.refs.length>1) ? "Save and go to next untagged" : "Save",
            button_save_and_next = $('<button class="btn btn-primary"></button>')
                .text(save_txt)
                .click(function(){self.save_and_next();}),
            button_reset_tags = $('<button class="btn">Remove all tags</button>')
                .click(function(){if(self.loaded_ref) self.loaded_ref.remove_tags();}),
            div_buttons = $('<div></div>')
                .append(['<h4>Tags for current reference</h4>',
                         this.$div_selected_tags,
                         button_save_and_next,
                         button_reset_tags,
                         this.saved_icon]);

        this.$div_reflist = $('<div class="span3"></div>');
        this._populate_reflist();

        this.$div_ref = $('<div class="span6"></div>').html([div_buttons, this.$div_error, this.$div_details]);

        this.$tags_content = this.load_tags()
                                 .on('hawc-tagClicked', function(e){
                                    var tag = $(e.target).data('d');
                                    self.loaded_ref.add_tag(tag);
                                 });

        var header = $('<h4>Available Tags</h4>');
        if(window.tag_edit_url){
            header.append('<a href="{0}" class="btn btn-primary pull-right">Edit Tags</a>'.printf(window.tag_edit_url));
        }

        this.$div_tags = $('<div class="span3"></div>')
                .html([header, this.$tags_content]);
        this.$div_content.html([this.$div_reflist, this.$div_ref, this.$div_tags]);

        this.$div_selected_tags.on('click', '.refTag', function(){
            self.loaded_ref.remove_tag($(this).data('d'));
        });

        this.$div_reflist.on('click', '.reference', function(){
            self.unload_reference();
            self.loaded_ref = $(this).data('d');
            self.load_reference();
        });
    },
    unload_reference: function(){
        if (this.loaded_ref){
            this._update_referencelist();
            this.loaded_ref.removeObserver(this);
            this.loaded_ref.deselect_name();
            this.loaded_ref = undefined;
        }
    },
    load_reference: function(){
        if (this.loaded_ref){
            this.loaded_ref.addObserver(this);
            this.loaded_ref.select_name();
            this.$div_details.html(this.loaded_ref.print_self());
            this.clear_errors();
            this._build_tagslist();
        }
    },
    _get_next_ref: function(){
        //Get the next reference that's untagged, unless none are available, If
        // none are available, just get the next one
        if(this.refs_untagged.length>0){
            this.loaded_ref = this.refs_untagged[0];
            this.load_reference();
        } else if (this.refs.length===1 && this.refs_tagged.length===1){
            // if we are editing a single reference, display
            this.loaded_ref = this.refs_tagged[0];
            this.load_reference();
        } else {
            this.set_references_complete();
        }
    },
    save_and_next: function(){

        var self = this,
            success = function(){
                self.saved_icon.fadeIn().fadeOut({complete: function(){
                    self.unload_reference();
                    self._get_next_ref();
                }});
            }, failure = function(){
                var txt = "An error occurred in saving; please wait a moment and retry. If the error persists please contact HAWC staff.",
                    div = $('<div>').attr("class", "alert alert-danger").text(txt);
                self.$div_error.html(div).prepend('<br>');
            };
        if (this.loaded_ref) this.loaded_ref.save(success, failure);
    },
    update: function(status){
        if(status==="TagTree"){
            this.$tags_content.html(this.load_tags());
        } else { //reference update
            this.load_reference();
        }
    },
    _populate_reflist: function(){
        var $refs_tagged = $('<div class="accordion-inner"></div>'),
            $refs_untagged = $('<div class="accordion-inner"></div>'),
            tagged = this.refs.filter(function(v){return v.data.tags.length>0;}),
            untagged = this.refs.filter(function(v){return v.data.tags.length===0;});

       tagged.forEach(function(v){$refs_tagged.append(v.print_name())});
       untagged.forEach(function(v){$refs_untagged.append(v.print_name())});

       var taggedbody = $('<div id="references_tagged" class="accordion-body collapse in"></div>')
                .append($refs_tagged),
           taggedgroup = $('<div class="accordion-group"></div>')
                .append('<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#references_lists" href="#references_tagged">Tagged</a></div>')
                .append(taggedbody);

       var untaggedbody = $('<div id="references_untagged" class="accordion-body collapse in"></div>')
                .append($refs_untagged),
           untaggedgroup = $('<div class="accordion-group"></div>')
                .append('<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#references_lists" href="#references_untagged">Untagged</a></div>')
                .append(untaggedbody);

       var acc = $('<div class="accordion" id="references_lists"></div>')
            .append(taggedgroup)
            .append(untaggedgroup);

       this.refs_tagged = tagged;
       this.refs_untagged = untagged;
       this.$refs_tagged = $refs_tagged;
       this.$refs_untagged = $refs_untagged;
       this.$div_reflist.html(['<h4>References</h4>', acc]);
    },
    _update_referencelist: function(){
        var self = this,
            has_tags = (this.loaded_ref.data.tags.length>0);
        if(has_tags){
            var in_untagged = false;
            this.refs_untagged.forEach(function(v, i){
                if(v === self.loaded_ref){
                    self.refs_untagged.splice(i,1);
                    in_untagged = true;
                }
            });
            if(in_untagged){
                this.refs_tagged.push(this.loaded_ref);
                this.loaded_ref.$list.detach();
                this.$refs_tagged.append(this.loaded_ref.$list);
            }
        }else{
            var in_tagged = false;
            this.refs_tagged.forEach(function(v, i){
                if(v === self.loaded_ref){
                    self.refs_tagged.splice(i,1);
                    in_tagged = true;
                }
            });
            if(in_tagged){
                this.refs_untagged.push(this.loaded_ref);
                this.loaded_ref.$list.detach();
                this.$refs_untagged.append(this.loaded_ref.$list);
            }
        }
    },
    _build_tagslist: function(){
        this.$div_selected_tags.html(this.loaded_ref.print_taglist());
    },
    load_tags: function(){
        return this.tagtree.get_nested_list();
    },
    clear_errors: function(){
        this.$div_error.empty();
    },
    set_references_complete: function(){

        var txt = "All references have been successfully tagged. Congratulations!",
            div = $('<div>').attr("class", "alert alert-success").text(txt);
        this.$div_details.html(div).prepend('<br>');

        this.$div_selected_tags.html("");
    }
};


var EditTagTreeContainer = function(tagtree, div){
    var self = this;
    this.$div = $(div);
    this.tagtree = tagtree;
    tagtree.addObserver(this);
    this._build_tree();

    $('#submit_new_tag').on('click', function(){
        if($('#tag_parent option:selected').data('d')){
            $('#tag_parent option:selected').data('d').add_child($('#tag_name').val());
        } else {
            tagtree.add_root_tag($('#tag_name').val());
        }
        $('#new_tag_form').modal('hide');
    });

    $('#submit_delete_tag').on('click', function(){
        $('#delete_tag option:selected').data('d').remove_self();
        $('#delete_tag_form').modal('hide');
    });
};
EditTagTreeContainer.prototype = {
    update: function(){
        this._build_tree();
    },
    _build_tree: function(){
        this.$div.html(this.tagtree.get_nested_list({"show_refs_count": false, "sortable": true}));
    }
};


var TagTree = function(data){
    Observee.apply(this, arguments);
    var self = this;
    this.tags = this._construct_tags(data[0], skip_root=true);
    this.dict = this._build_dictionary();
    this.observers = [];
};
_.extend(TagTree.prototype, Observee.prototype, {
    add_root_tag: function(name){
        var self = this,
            data = {"content": "tag",
                    "status": "add",
                    "name": name};
        $.post('.', data, function(v) {
            if (v.status === "success"){
                self.tags.push(new NestedTag(v.node[0], 0, self));
                self.tree_changed();
            }
        });
    },
    get_nested_list: function(options){
        // builds a nested list
        var div = $('<div></div>');
        this.tags.forEach(function(v){v.get_nested_list_item(div, "", options);});
        return div;
    },
    get_options: function(){
        var list = [];
        this.tags.forEach(function(v){v.get_option_item(list);});
        return list;
    },
    _build_dictionary: function(){
        var dict = {};
        this.tags.forEach(function(v){v._append_to_dict(dict);});
        return dict;
    },
    _construct_tags: function(data, skip_root){
        // unpack our tags and construct NestedTag objects
        var self = this,
            tags = [];
        if(skip_root){
            if(data.children){
                data.children.forEach(function(v){
                    tags.push(new NestedTag(v, 0, self));
                });
            }
        } else {
            tags.push(new NestedTag(v, 0, self));
        }
        return tags;
    },
    tree_changed: function(){
        this.dict = this._build_dictionary();
        this.notifyObservers('TagTree');
    },
    remove_child: function(tag){
        this.tags.splice_object(tag);
        delete tag;
    },
    add_references: function(references){
        var dict = this.dict;
        for(var key in this.dict){
            this.dict[key].references = [];
        }
        references.forEach(function(v){
            dict[v.tag_id].references.push(v.content_object_id);
        });
        this.get_refs_count();
    },
    build_top_level_node: function(name){
        //transform top-level of tagtree to resemble node for plotting
        this.children = this.tags;
        this.data = {"name": name};

        //special case for reference count
        refs = [];
        this.children.forEach(function(v){v.get_references(refs);});
        this.data.reference_count = refs.getUnique().length;
    },
    get_refs_count: function(name){
        this.tags.forEach(function(v){v.get_reference_count();});
    },
    view_untagged_references: function(reference_viewer){
        var url = '/lit/assessment/{0}/references/untagged/json/'.printf(window.assessment_pk);
        if (window.search_id) url += "?search_id={0}".printf(window.search_id);

        $.get(url, function(results){
            if(results.status=="success"){
                refs = [];
                results.refs.forEach(function(datum){
                    refs.push(new Reference(datum, window.tagtree));
                });
                reference_viewer.set_references(refs);
            } else {
                reference_viewer.set_error();
            }
        });
    },
});


var NestedTag = function(item, level, tree, parent){
    Observee.apply(this, arguments);
    var self = this,
        children = [];
    this.observers= [];
    this.parent = parent;
    this.data = item.data;
    this.data.pk = item.id;
    this.level = level;
    this.tree = tree;
    if(item.children){
        item.children.forEach(function(v){
            children.push(new NestedTag(v, level+1, tree, self));
        });
    }
    this.children = children;
    return this;
};
_.extend(NestedTag.prototype, Observee.prototype, {
    get_nested_list_item: function(parent, padding, options){
        var div = $('<div></div>'),
            collapse = $('<span class="nestedTagCollapser"></span>').appendTo(div),
            txtspan = $('<p class="nestedTag"></p>'),
            text = '{0}{1}'.printf(padding, this.data.name);

        if(options && options.show_refs_count) text += " ({0})".printf(this.get_reference_count());
        txtspan.text(text)
               .appendTo(div)
               .data('d', this)
               .on('click', function(){$(this).trigger('hawc-tagClicked');});
        parent.append(div);

        if(this.children.length>0){
            var toggle = $('<a>')
                .attr('title', "Collapse tags: {0}".printf(this.data.name))
                .attr('data-toggle', "collapse")
                .attr('href', "#collapseTag{0}".printf(this.data.pk))
                .data('expanded', true)
                .data('name', this.data.name)
                .on('click', function(){
                    var self = toggle;
                    self.data('expanded', !self.data('expanded'));
                    if (self.data('expanded')){
                        span.attr('class', 'icon-minus');
                        self.attr('title', 'Collapse tags: {0}'.printf(self.data('name')));
                    } else {
                        span.attr('class', 'icon-plus');
                        self.attr('title', 'Expand tags: {0}'.printf(self.data('name')));
                    }
                }),
                span = $('<span class="icon-minus"></span>').appendTo(toggle);
            toggle.appendTo(collapse);

            var nested = $('<div id="collapseTag{0}" class="in collapse"></div>'.printf(this.data.pk)).appendTo(div);
            this.children.forEach(function(v){v.get_nested_list_item(nested, padding + "   ", options);});
            if (options && options.sortable){
                nested.sortable({
                    containment: parent,
                    start: function(event, ui) {
                        var start_pos = ui.item.index();
                        ui.item.data('start_pos', start_pos);
                    },
                    stop: function(event, ui) {
                        var start_pos = ui.item.data('start_pos'),
                            offset = ui.item.index() - start_pos;
                        if (offset !== 0) $(this).trigger('hawc-tagMoved', [ui.item, offset]);
                    }
                });
            }
        }

        return parent;
    },
    get_reference_count: function(){
        this.data.reference_count = this.get_references([]).getUnique().length;
        this.children.forEach(function(v){v.get_reference_count();});
        return this.data.reference_count;
    },
    get_references: function(list){
        // get references and child references
        refs = list.concat(this.references);
        if (this.children){
            this.children.forEach(function(v){v.get_references(refs);});
        }
        if (this._children){
            this._children.forEach(function(v){v.get_references(refs);});
        }
        return refs.getUnique();
    },
    get_reference_objects_by_tag: function(reference_viewer){
        var url = '/lit/assessment/{0}/references/{1}/json/'
            .printf(window.assessment_pk, this.data.pk);
        if (window.search_id) url += "?search_id={0}".printf(window.search_id);

        $.get(url, function(results){
            if(results.status=="success"){
                refs = [];
                results.refs.forEach(function(datum){refs.push(new Reference(datum, window.tagtree));});
                reference_viewer.set_references(refs);
            } else {
                reference_viewer.set_error();
            }
        });
    },
    get_option_item: function(lst){
        lst.push($('<option value="{0}">{1}{2}</option>'
                    .printf(this.data.pk, Array(this.level+1).join('&nbsp;&nbsp;'), this.data.name))
                    .data('d', this));
        this.children.forEach(function(v){v.get_option_item(lst);});
        return lst;
    },
    _append_to_dict: function(dict){
        dict[this.data.pk] = this;
        this.children.forEach(function(v){v._append_to_dict(dict);});
    },
    get_full_name: function(){
        if(this.parent && this.parent.get_full_name){
            return this.parent.get_full_name() + ' ➤ ' + this.data.name;
        } else {
            return this.data.name;
        }
    },
    add_child: function(name){
        var self = this,
            data = {"status": "add",
                    "parent_pk": this.data.pk,
                    "name": name};
        $.post('.', data, function(v){
            if (v.status === "success"){
                self.children.push(new NestedTag(v.node[0], self.level+1, self.tree, self));
                self.tree.tree_changed();
            }
        });
    },
    remove_self: function(){
        this.children.forEach(function(v){v.remove_self();});
        var self = this,
            data = {"status": "remove",
                    "pk": this.data.pk};
        $.post('.', data, function(v){
            console.log(v);
            if (v.status === "success"){
                self.notifyObservers({"event": "tag removed", "object": self});
                if(self.parent){
                    self.parent.remove_child(self);
                } else {
                    self.tree.remove_child(self);
                }
                self.tree.tree_changed();
            }
        });
    },
    move_self: function(offset){
        var self = this,
            lst = this.parent.children,
            index = lst.indexOf(this);

        // update locally
        lst.splice(index+offset, 0, lst.splice(index, 1)[0]);

        // push changes to server
        data = {"status": "move",
                "pk": this.data.pk,
                "offset": offset};

        $.post('.', data, function(v){
            if (v.status === "success") self.tree.tree_changed();
        });
    },
    remove_child: function(tag){
        this.children.splice_object(tag);
        delete tag;
    }
});


var TagTreeViz = function(tagtree, plot_div, title, downloadURL, options){
    // Displays multiple-dose-response details on the same view and allows for
    // custom visualization of these plots
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.options = options || {};
    this.set_defaults();
    this.plot_div = $(plot_div);
    this.tagtree = tagtree;
    this.title_str = title;
    this.downloadURL = downloadURL;
    this.modal = new HAWCModal();
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(TagTreeViz.prototype, D3Plot.prototype, {
    build_plot: function(){
        this.plot_div.html('');
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.draw_visualization();
        this.add_menu();
        this.trigger_resize();
    },
    get_plot_sizes: function(){
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
            menu_spacing) + 'px'});
    },
    set_defaults: function(){
        this.padding = {top:40, right:5, bottom:5, left:100};
        this.w = 1280 - this.padding.left - this.padding.right;
        this.h = 800 - this.padding.top - this.padding.bottom;
        this.minimum_radius = 8;
        this.maximum_radius = 30;
        if(!this.options.build_plot_startup){this.options.build_plot_startup=true;}
    },
    draw_visualization: function(){
        var i = 0,
            root = this.tagtree,
            vis = this.vis,
            tree = d3.layout.tree()
                    .size([this.h, this.w]),
            diagonal = d3.svg.diagonal()
                    .projection(function(d){return [d.y, d.x];}),
            self = this;

        root.x0 = this.h / 2;
        root.y0 = 0;

        this.add_title();

        var radius_scale = d3.scale.pow().exponent(0.5)
            .domain([0, root.data.reference_count])
            .range([this.minimum_radius, this.maximum_radius]);

        function toggleAll(d){
            if (d.children){
                d.children.forEach(toggleAll);
                toggle(d);
            }
        }

        function toggle(d){
            if((d.children) && (d.children.length>0)) {
                d._children = d.children;
                d.children = null;
            }else{
                d.children = d._children;
                d._children = null;
            }
        }

        root.children.forEach(toggleAll);
        update(root);

        function fetch_references(nested_tag){
            var title = '<h4>{0}</h4>'.printf(nested_tag.data.name),
                div = $('<div id="references_div"></div'),
                options = {tag: nested_tag, download_url: self.downloadURL},
                refviewer = new ReferencesViewer(div, options)
            self.modal
                .addHeader(title)
                .addBody(div)
                .addFooter("")
                .show({maxWidth: 800});
            nested_tag.get_reference_objects_by_tag(refviewer);
        }

        function update(source) {
            var duration = d3.event && d3.event.altKey ? 5000 : 500;

            // Compute the new tree layout.
            var nodes = tree.nodes(root).reverse();

            // Normalize for fixed-depth.
            nodes.forEach(function(d) { d.y = d.depth * 180; });

            // Update the nodes…
            var node = vis.selectAll("g.tagnode")
                        .data(nodes, function(d) { return d.id || (d.id = ++i); });

            // Enter any new nodes at the parent's previous position.
            var nodeEnter = node.enter().append("svg:g")
                        .attr("class", "tagnode")
                        .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
                        .on("click", function(d){
                            if(d3.event.ctrlKey || d3.event.metaKey){
                                if (d.depth == 0){
                                   alert("Cannot view details on root-node.");
                                } else {
                                    fetch_references(d);
                                }
                            } else {
                                toggle(d);
                                update(d);
                            }
                        });

            nodeEnter.append("svg:circle")
                    .attr("r", 1e-6)
                    .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

            nodeEnter.append("svg:text")
                    .attr("x", 0)
                    .attr("dy", function(d){return radius_scale(d.data.reference_count)+15;})
                    .attr("class", "node_name")
                    .attr("text-anchor", "middle")
                    .text(function(d) { return d.data.name; })
                    .style("fill-opacity", 1e-6);

            nodeEnter.append("svg:text")
                    .attr("x", 0)
                    .attr("dy", "3.5px")
                    .attr("class", "node_value")
                    .attr("text-anchor", "middle")
                    .text(function(d) { return d.data.reference_count; })
                    .style("fill-opacity", 1e-6);

            // Transition nodes to their new position.
            var nodeUpdate = node.transition()
                    .duration(duration)
                    .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

            nodeUpdate.select("circle")
                    .attr("r", function(d){return radius_scale(d.data.reference_count);})
                    .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

            nodeUpdate.selectAll("text")
                    .style("fill-opacity", 1);

            // Transition exiting nodes to the parent's new position.
            var nodeExit = node.exit().transition()
                    .duration(duration)
                    .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
                    .remove();

            nodeExit.select("circle")
                    .attr("r", 1e-6);

            nodeExit.select("text")
                    .style("fill-opacity", 1e-6);

            // Update the links…
            var link = vis.selectAll("path.tagslink")
                    .data(tree.links(nodes), function(d) { return d.target.id; });

            // Enter any new links at the parent's previous position.
            link.enter().insert("svg:path", "g")
                .attr("class", "tagslink")
                .attr("d", function(d) {
                    var o = {x: source.x0, y: source.y0};
                    return diagonal({source: o, target: o});
                })
                .transition()
                    .duration(duration)
                    .attr("d", diagonal);

            // Transition links to their new position.
            link.transition()
                    .duration(duration)
                    .attr("d", diagonal);

            // Transition exiting nodes to the parent's new position.
            link.exit().transition()
                .duration(duration)
                .attr("d", function(d) {
                    var o = {x: source.x, y: source.y};
                    return diagonal({source: o, target: o});
                })
                .remove();

            // Stash the old positions for transition.
            nodes.forEach(function(d) {
                d.x0 = d.x;
                d.y0 = d.y;
            });
        }

        // this.vis.append('svg:text')
        //     .attr('x', -this.padding['left']+5)
        //     .attr('y', this.h-5)
        //     .text("CTRL-click to view references associated with an node.");
    }
});
