Array.prototype.getUnique = function(){
   var u = {}, a = [];
   for(var i = 0, l = this.length; i < l; ++i){
      if(u.hasOwnProperty(this[i])){continue;}
      a.push(this[i]);
      u[this[i]] = 1;
   }
   return a;
};


var Reference = function(data, tagtree){
    var self = this,
        tag_ids = data.tags;

    this.observers = [];
    this.data = data;
    this.data.tags = [];
    tag_ids.forEach(function(v){self.add_tag(tagtree.dict[v]);});
};

Reference.no_authors_text = '[No authors listed]';

Reference.prototype.addObserver = function(obs){
    this.observers.push(obs);
};

Reference.prototype.removeObserver = function(obs){
    this.observers.splice_object(obs);
};

Reference.prototype.notifyObservers = function(status){
    this.observers.forEach(function(v, i){
        v.update(status);
    });
};

Reference.prototype.print_self = function(show_taglist){
    var taglist = show_taglist || false;

    var content = ['<h4>Reference details:</h4>',
                   '<p class="ref_small">{0}</p>'.printf(this.data.journal),
                   '<p class="ref_title">{0}</p>'.printf(this.data.title),
                   '<p class="ref_small">{0}</p>'.printf(this.data.authors || Reference.no_authors_text)];
    if(taglist){
        content = content.concat(this.print_taglist());
    }
    content.push('<p>{0}</p>'.printf(this.data.abstract));
    this.data.identifiers.forEach(function(v,i){
        if(v.url){
            content.push('<p class="ref_small">{0} link: <a target="_blank" href="{1}">{2}</a></p>'
                         .printf(v.database, v.url, v.id));
        }
    });
    return content;
};

Reference.prototype.print_taglist = function(){
    var tags = [];
    this.data.tags.forEach(function(v){
        tags.push($('<span title="click to remove" class="ref_tag">{0}</span>'.printf(v.get_full_name())).data('d', v));
    });
    return tags;
};

Reference.prototype.print_name = function(){
    this.$list = $('<p class="reference">{0} {1}</p>'.printf(this.data.authors || Reference.no_authors_text,
                                                             this.data.year || ""))
                                                     .data('d', this);
    return this.$list;
};

Reference.prototype.select_name = function(){
    this.$list.addClass("selected");
};

Reference.prototype.deselect_name = function(){
    this.$list.removeClass("selected");
};

Reference.prototype.print_div_row = function(){

    var div = $('<div></div>'),
        authors = $('<p class="ref_small">{0} {1}</p>'.printf(
                        this.data.authors || Reference.no_authors_text,
                        this.data.year || "")),
        abs_btn = this.get_abstract_button(div),
        edit_btn = this.get_edit_button();

    if(abs_btn || edit_btn){
        var ul = $('<ul class="dropdown-menu">');

        if (abs_btn) ul.append($('<li>').append(abs_btn));
        if (edit_btn) ul.append($('<li>').append(edit_btn));

        $('<div class="btn-group pull-right">')
            .append('<a class="btn btn-small dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>')
            .append(ul)
            .appendTo(authors);
    }

    return div.html([
        '<hr>',
        authors,
        '<p class="ref_title">{0}</p>'.printf(this.data.title),
        '<p class="ref_small">{0}</p>'.printf(this.data.journal),
        '<p class="abstracts collapse" >{1}</p>'.printf(this.data.pk, this.data.abstract),
    ].concat(this.print_taglist()));
};

Reference.prototype.get_abstract_button = function(div){
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
};

Reference.prototype.get_edit_button = function(){
    // get edit button if editing enabled, or return undefined
    if(window.canEdit){
        return $('<a>')
            .text('Edit tags')
            .attr('href', this.edit_tags_url())
            .attr('target', '_blank');
    }
};

Reference.prototype.add_tag = function(tag){
    var tag_already_exists = false;
    this.data.tags.forEach(function(v){if(tag===v){tag_already_exists=true;}});
    if(tag_already_exists) return;
    this.data.tags.push(tag);
    tag.addObserver(this);
    this.notifyObservers();
};

Reference.prototype.edit_tags_url = function(){
    return "/lit/reference/{0}/tag/".printf(this.data.pk);
};

Reference.prototype.remove_tag = function(tag){
    this.data.tags.splice_object(tag);
    tag.removeObserver(this);
    this.notifyObservers();
};

Reference.prototype.remove_tags = function(){
    this.data.tags = [];
    this.notifyObservers();
};

Reference.prototype.save = function(success, failure){
    var data = {"pk": this.data.pk,
                "tags": this.data.tags.map(function(v){return v.data.pk;})};
    $.post('.', data, function(v) {
        return (v.status==="success") ? success() : failure();
    }).fail(failure);
};

Reference.prototype.update = function(status){
    if (status.event =="tag removed"){this.remove_tag(status.object);}
};


var ReferencesViewer = function($div, options){
    this.options = options;
    this.$div = $div;

    this.$table_div = $('<div id="references_detail_block"></div>');
    this.$div.html([this._print_header(), this.$table_div]);
    this._set_loading_view();
};

ReferencesViewer.prototype.set_references = function(refs){
    this.refs = refs;
    this._build_reference_table();
};

ReferencesViewer.prototype.set_error = function(){
    this.$table_div.html('<p>An error has occured</p>');
};

ReferencesViewer.prototype._print_header = function(){
    var h3 = $('<h3></h3>')
        self = this;
    if(this.options.fixed_title){
        h3.text(this.options.fixed_title);
    } else {
        var tag_name = this.options.tag.get_full_name(),
            actions = '<div class="btn-group pull-right">' +
                        '<a class="btn btn-primary dropdown-toggle" data-toggle="dropdown">Actions <span class="caret"></span></a>' +
                        '<ul class="dropdown-menu">' +
                          '<li><a href="{0}?tag_pk={1}">Download references</a></li>'.printf(this.options.download_url, this.options.tag.data.pk) +
                          '<li><a href="#" class="show_abstracts">Show all abstracts</a></li>' +
                        '</ul>' +
                      '</div>';
        h3.text("References tagged ")
          .append("<span class='ref_tag'>{0}</span>".printf(tag_name))
          .append(actions)
          .on('click', '.show_abstracts', function(){
            var sel = $(this);
            if(sel.text() === "Show all abstracts"){
                self.$div.find('.abstracts').collapse('show');
                sel.text("Hide all abstracts");
                self.$div.find('.abstractToggle').text('Hide abstract');
            } else {
                self.$div.find('.abstracts').collapse('hide');
                sel.text("Show all abstracts");
                self.$div.find('.abstractToggle').text('Show abstract');
            }
          });
    }
    return h3;
};

ReferencesViewer.prototype._set_loading_view = function(){
    this.$table_div.html('<p>Loading: <img src="/static/img/loading.gif"/></p>');
};

ReferencesViewer.prototype._build_reference_table = function(){
    var content = [];
    this.refs.forEach(function(v){
        content.push(v.print_div_row());
    });
    this.$table_div.html(content);
};


var EditReferenceContainer = function(refs, tagtree, settings){
    this.refs = refs;
    this.tagtree = tagtree;
    this.tagtree.addObserver(this);
    this.$div_content = $(settings.content_div);
    // build containers and load first reference
    this._build_containers();
    this._get_next_ref();
    this.load_reference();
};

EditReferenceContainer.prototype._build_containers = function(){

    this.$div_selected_tags = $("<div class='well well-small'></div>");
    this.$div_details = $('<div></div>');
    this.$div_error = $('<div></div>');
    this.saved_icon = $('<span class="btn litSavedIcon" style="display: none;">Saved!</span>');

    var self = this,
        save_txt = (this.refs.length>1) ? "Save and go to ext untagged" : "Save",
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

    this.$div_selected_tags.on('click', '.ref_tag', function(){
        self.loaded_ref.remove_tag($(this).data('d'));
    });

    this.$div_reflist.on('click', '.reference', function(){
        self.unload_reference();
        self.loaded_ref = $(this).data('d');
        self.load_reference();
    });
};

EditReferenceContainer.prototype.unload_reference = function(){
    if (this.loaded_ref){
        this._update_referencelist();
        this.loaded_ref.removeObserver(this);
        this.loaded_ref.deselect_name();
        this.loaded_ref = undefined;
    }
};

EditReferenceContainer.prototype.load_reference = function(){
    if (this.loaded_ref){
        this.loaded_ref.addObserver(this);
        this.loaded_ref.select_name();
        this.$div_details.html(this.loaded_ref.print_self());
        this.clear_errors();
        this._build_tagslist();
    }
};

EditReferenceContainer.prototype._get_next_ref = function(){
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
};

EditReferenceContainer.prototype.save_and_next = function(){

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
};

EditReferenceContainer.prototype.update = function(status){
    if(status==="TagTree"){
        this.$tags_content.html(this.load_tags());
    } else { //reference update
        this.load_reference();
    }
};

EditReferenceContainer.prototype._populate_reflist = function(){
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
};

EditReferenceContainer.prototype._update_referencelist = function(){
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
};

EditReferenceContainer.prototype._build_tagslist = function(){
    this.$div_selected_tags.html(this.loaded_ref.print_taglist());
};

EditReferenceContainer.prototype.load_tags = function(){
    return this.tagtree.get_nested_list();
};

EditReferenceContainer.prototype.clear_errors = function(){
    this.$div_error.empty();
};

EditReferenceContainer.prototype.set_references_complete = function(){

    var txt = "All references have been successfully tagged. Congratulations!",
        div = $('<div>').attr("class", "alert alert-success").text(txt);
    this.$div_details.html(div).prepend('<br>');

    this.$div_selected_tags.html("");
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

EditTagTreeContainer.prototype.update = function(){
    this._build_tree();
};

EditTagTreeContainer.prototype._build_tree = function(){
    this.$div.html(this.tagtree.get_nested_list({"show_refs_count": false, "sortable": true}));
};


var TagTree = function(data){
    var self = this;
    this.tags = this._construct_tags(data[0], skip_root=true);
    this.dict = this._build_dictionary();
    this.observers = [];
};

TagTree.prototype.add_root_tag = function(name){
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
};

TagTree.prototype.get_nested_list = function(options){
    // builds a nested list
    var div = $('<div></div>');
    this.tags.forEach(function(v){v.get_nested_list_item(div, "", options);});
    return div;
};

TagTree.prototype.get_options = function(){
    var list = [];
    this.tags.forEach(function(v){v.get_option_item(list);});
    return list;
};

TagTree.prototype._build_dictionary = function(){
    var dict = {};
    this.tags.forEach(function(v){v._append_to_dict(dict);});
    return dict;
};

TagTree.prototype._construct_tags = function(data, skip_root){
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
};

TagTree.prototype.addObserver = function(obs){
    this.observers.push(obs);
};

TagTree.prototype.removeObserver = function(obs){
    this.observers.splice_object(obs);
};

TagTree.prototype.notifyObservers = function(status){
    this.observers.forEach(function(v, i){
        v.update(status);
    });
};

TagTree.prototype.tree_changed = function(){
    this.dict = this._build_dictionary();
    this.notifyObservers('TagTree');
};

TagTree.prototype.remove_child = function(tag){
    this.tags.splice_object(tag);
    delete tag;
};

TagTree.prototype.add_references = function(references){
    var dict = this.dict;
    for(var key in this.dict){
        this.dict[key].references = [];
    }
    references.forEach(function(v){
        dict[v.tag_id].references.push(v.content_object_id);
    });
    this.get_refs_count();
};

TagTree.prototype.build_top_level_node = function(name){
    //transform top-level of tagtree to resemble node for plotting
    this.children = this.tags;
    this.data = {"name": name};

    //special case for reference count
    refs = [];
    this.children.forEach(function(v){v.get_references(refs);});
    this.data.reference_count = refs.getUnique().length;
};

TagTree.prototype.get_refs_count = function(name){
    this.tags.forEach(function(v){v.get_reference_count();});
};


var NestedTag = function(item, level, tree, parent){
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

NestedTag.prototype.get_nested_list_item = function(parent, padding, options){
    var div = $('<div></div>'),
        collapse = $('<span class="nestedTagCollapser"></span>').appendTo(div),
        txtspan = $('<span class="nested-tag"></span>'),
        text = '{0}{1}'.printf(padding, this.data.name);

    if(options && options.show_refs_count) text += " ({0})".printf(this.get_reference_count());
    txtspan.text(text)
           .appendTo(div)
           .data('d', this)
           .on('click', function(){$(this).trigger('hawc-tagClicked');});
    parent.append(div);

    if(this.children.length>0){
        var toggle = $('<a></a>')
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
};

NestedTag.prototype.get_reference_count = function(){
    this.data.reference_count = this.get_references([]).getUnique().length;
    this.children.forEach(function(v){v.get_reference_count();});
    return this.data.reference_count;
};

NestedTag.prototype.get_references = function(list){
    // get references and child references
    refs = list.concat(this.references);
    if (this.children){
        this.children.forEach(function(v){v.get_references(refs);});
    }
    if (this._children){
        this._children.forEach(function(v){v.get_references(refs);});
    }
    return refs.getUnique();
};

NestedTag.prototype.get_reference_objects = function(reference_viewer){
    var url = '/lit/assessment/{0}/references/json/'.printf(window.assessment_pk),
        data = {'pks': this.get_references([])};
    $.get(url, data, function(results){
        if(results.status=="success"){
            refs = [];
            results.refs.forEach(function(datum){refs.push(new Reference(datum, window.tagtree));});
            reference_viewer.set_references(refs);
        } else {
            reference_viewer.set_error();
        }
    });
};

NestedTag.prototype.get_option_item = function(lst){
    lst.push($('<option value="{0}">{1}{2}</option>'
                .printf(this.data.pk, Array(this.level+1).join('&nbsp;&nbsp;'), this.data.name))
                .data('d', this));
    this.children.forEach(function(v){v.get_option_item(lst);});
    return lst;
};

NestedTag.prototype._append_to_dict = function(dict){
    dict[this.data.pk] = this;
    this.children.forEach(function(v){v._append_to_dict(dict);});
};

NestedTag.prototype.get_full_name = function(){
    if(this.parent && this.parent.get_full_name){
        return this.parent.get_full_name() + '/' + this.data.name;
    } else {
        return this.data.name;
    }
};

NestedTag.prototype.add_child = function(name){
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
};

NestedTag.prototype.remove_self = function(){
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
};

NestedTag.prototype.move_self = function(offset){
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
};

NestedTag.prototype.remove_child = function(tag){
    this.children.splice_object(tag);
    delete tag;
};

NestedTag.prototype.addObserver = function(obs){
    this.observers.push(obs);
};

NestedTag.prototype.removeObserver = function(obs){
    this.observers.splice_object(obs);
};

NestedTag.prototype.notifyObservers = function(status){
    this.observers.forEach(function(v, i){
        v.update(status);
    });
};
