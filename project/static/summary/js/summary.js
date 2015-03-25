var SummaryTextTree = function(options, callback){
    var self = this;
    this.options = options;
    this.root = undefined;
    this.get_summaries();
    if(callback){this.callback=callback;}
};
SummaryTextTree.prototype = {
    get_summaries: function(){
        var self = this,
            url = '/summary/assessment/{0}/summaries/json/'.printf(this.options.assessment_id);
        $.get(url, function(d){
            self.root = new SummaryText(d[0], 1, self, 0);
            if((self.root.data.comments) && (self.root.data.comments.length>0)){
                self._unpack_comments();
            }
            if(self.options.mode=="read"){
                self._update_read();
            } else if (self.options.mode==="modify"){
                self._update_modified();
            }
        });
    },
    _update_read: function(){
        this.render_docheaders();
        this.render_doctext();
        this.enable_affix();
        if(this.callback){this.callback();}
    },
    _unpack_comments: function(){
        var self = this;
        this.root.data.comments.forEach(function(v){
            self.root._add_comment(v);
        });
    },
    _update_modified: function(){
        this.options.update_textdiv.fadeOut();
        this.render_doctree();
        this.set_modify_events();
        if(this.callback){this.callback();}
    },
    render_docheaders: function(){
        var contents = [];
        var txt = '<li><a href="#"><i>No summary-text is available.</i></a></li>';
        if (this.root.children.length===0){
            contents.push(txt);
        } else {
            this.root.children.forEach(function(v){
                v.render_header(contents);
            });
        }
        this.options.read_headers_ul.html(contents);
    },
    render_doctext: function(){
        var contents = [];
        if (this.root.children.length===0){
            contents.push('<p>No summary-text is available.</p>');
        } else {
            this.root.children.forEach(function(v){
                v.render_body(contents);
            });
        }
        this.options.read_text_div.html(contents);
    },
    update_textdiv: function(obj){

        var self = this,
            new_object = (obj===undefined),
            parent_options = function(summary_text, new_object){
                var lst = [],
                    select = self.options.update_textdiv.find('select#id_parent');
                self.root.get_option_item(lst);
                select.html(lst);
                if(!new_object){
                    select.find('option[value="{0}"]'.printf(summary_text.parent.id)).prop('selected', true);
                }
            }, sibling_options = function(summary_text, new_object){
                var select = self.options.update_textdiv.find('select#id_sibling'),
                    text_node_id = parseInt(self.options.update_textdiv.find('select#id_parent option:selected').val(), 10),
                    lst =['<option value="-1">(none)</option>'],
                    parent = self.get_summarytext_node(text_node_id);
                parent.get_children_option_items(lst);
                select.html(lst);
                if(!new_object){
                    select.find('option[value="{0}"]'.printf(summary_text.get_prior_sibling_id())).prop('selected', true);
                }
            }, load_contents = function(obj){
                self.options.update_textdiv.find('#id_delete').prop('checked', false);
                if (obj){
                    self.options.update_textdiv.find('#id_title').val(obj.data.title);
                    self.options.update_textdiv.find('#id_slug').val(obj.data.slug);
                    self.options.update_smart_tag_editor.setValue(obj.data.text);
                    self.options.update_textdiv.find('#id_text').val(obj.data.text);
                    self.options.update_textdiv.find('#id_id').val(obj.id);
                } else {
                    self.options.update_textdiv.find('#id_title').val("");
                    self.options.update_textdiv.find('#id_slug').val("");
                    self.options.update_smart_tag_editor.setValue("");
                    self.options.update_textdiv.find('#id_id').val("-1");
                }
                SmartTag.initialize_tags($(self.options.update_smart_tag_editor.composer.element));
            },
            legend_text;

        if (obj){
            self._show_move_node_options(false);
            legend_text = 'Update {0}'.printf(obj.data.title);
            load_contents(obj);
        } else {
            obj = self.root;
            self._show_move_node_options(true);
            legend_text = 'Create new section';
            load_contents();
        }

        parent_options(obj, new_object);
        sibling_options(obj, new_object);
        self.options.update_textdiv.find('legend.summary_text_legend').text(legend_text);
        self.options.update_textdiv.fadeIn();
        self.options.update_textdiv.find('select#id_parent')
            .on('change', function(){sibling_options(obj, new_object);});
    },
    _show_move_node_options: function(show){
        if(show){
            this.options.update_textdiv.find("select#id_parent").parent().parent().fadeIn();
            this.options.update_textdiv.find("select#id_sibling").parent().parent().fadeIn();
        } else {
            this.options.update_textdiv.find("select#id_parent").parent().parent().fadeOut();
            this.options.update_textdiv.find("select#id_sibling").parent().parent().fadeOut();
        }
    },
    set_modify_events: function(){
        var self = this;

        this.options.update_new.unbind()
            .on('click', function(){self.update_textdiv();});

        this.options.update_move.unbind()
            .on('click', function(){self._show_move_node_options(true);});

        this.options.update_textdiv.find('form').unbind()
            .submit(function(e){e.preventDefault(); self.submit();});

        this.options.update_delete.unbind()
            .on('click', function(){
                self.options.update_textdiv.find('form #id_delete').prop('checked', true);
                self.submit();
            });

        this.options.update_doctree.unbind()
            .on('click', '.summary_toc', function(){
                self.update_textdiv($(this).data('d'));
            });
    },
    render_doctree: function(){
        var contents=[];
        if (this.root.children.length===0){
            contents.push('<p><i>No contents.</i></p>');
        } else {
            this.root.children.forEach(function(v){
                v.render_tree(contents);
            });
        }
        this.options.update_doctree.html(contents);
    },
    get_summarytext_node: function(id){
        var node,
            get_id = function(st, id){
                if(st.id===id){node = st; return;}
                st.children.forEach(function(v){get_id(v, id);});
            };

        get_id(this.root, id);
        return node;
    },
    submit: function(){
        var self = this,
            smart_tag_object = this.options.update_smart_tag_editor,
            post = function(){
                smart_tag_object.synchronizer.sync();
                var form = self.options.update_textdiv.find('form'),
                    data = form.serialize();
                $.post('.', data, function(d){
                    if (d.status=="ok"){
                        self.root = new SummaryText(d.content[0], 1, self);
                        self._update_modified();
                    } else {
                        console.log(d.content);
                    }
                });
            };

        $.when(InlineRendering.reset_renderings($(smart_tag_object.composer.doc)))
            .done(post());
    },
    enable_affix: function(){
        $('.affix-sidenav a').click(function(e){
            var href = $(this).attr("href"),
                offsetTop = href === "#" ? 0 : $(href).offset().top-65;
        $('html, body').stop().animate({scrollTop: offsetTop}, 300);
            e.preventDefault();
        });

        $('[data-spy="scroll"]').each(function () {
            var $spy = $(this).scrollspy('refresh');
        });
    }
};


var SummaryText = function(obj, depth, tree, sibling_id, parent){
    this.parent = parent;
    this.tree = tree;
    this.depth = depth;
    this.id = obj.id;
    this.data = obj.data;
    if (tree.options.commenting_public || tree.options.commenting_enabled){
        this.comment_manager = new CommentManager({"object_type": "summary_text",
                                                   "object_id": this.id,
                                                   "commenting_public": this.tree.options.commenting_public,
                                                   "commenting_enabled": this.tree.options.commenting_enabled,
                                                   "user": this.tree.options.user,
                                                   "fetch_comments": false}, this);
    }
    this.section_label = (parent) ? (this.parent.section_label +
                                     (sibling_id+1).toString() + ".") : ("");

    var self = this,
        children = [];
    if(obj.children){
        obj.children.forEach(function(child, i){
            children.push(new SummaryText(child, depth+1, tree, i, self));
        });
    }
    this.children = children;
};
SummaryText.prototype = {
    get_option_item: function(lst){
        var title = (this.depth===1) ? "(document root)" : this.data.title;
        lst.push($('<option value="{0}">{1}{2}</option>'
                    .printf(this.id, Array(this.depth).join('&nbsp;&nbsp;'), title))
                    .data('d', this));
        this.children.forEach(function(v){v.get_option_item(lst);});
    },
    get_children_option_items: function(lst){
        this.children.forEach(function(v){
            lst.push('<option value="{0}">{1}</option>'.printf(v.id, v.data.title));
        });
    },
    render_tree: function(lst){
        lst.push($('<p class="summary_toc">{0}{1}</p>'.printf(
                                          this.get_tab_depth(),
                                          this.data.title)).data('d', this));
        this.children.forEach(function(v){v.render_tree(lst);});
    },
    get_tab_depth: function(){
        return Array(this.depth-1).join('&nbsp;&nbsp;');
    },
    print_section: function(){

        var div = $('<div id="{0}"></div>'.printf(this.data.slug)),
            header = $('<h{0}>{1} {2}</h{3}>'.printf(this.depth,
                                                     this.section_label,
                                                     this.data.title,
                                                     this.depth)),
            content = $('<div>{0}</div>'.printf(this.data.text));

        if(this.comment_manager){this.comment_manager.build_popup_button(header);}
        return div.append(header, content);
    },
    render_header: function(lst){
        lst.push('<li><a href="#{0}">{1}{2} {3}<i class="icon-chevron-right"></i></a></li>'.printf(
                this.data.slug,
                this.get_tab_depth(),
                this.section_label,
                this.data.title));
        this.children.forEach(function(v){v.render_header(lst);});
    },
    render_body: function(lst){
        lst.push(this.print_section());
        this.children.forEach(function(v){v.render_body(lst);});
    },
    get_prior_sibling_id: function(){
        var self=this,
            result = -1;
        if(this.parent){
            this.parent.children.forEach(function(v, i){
                if (v.id===self.id && i>0){result = self.parent.children[i-1].id;}
            });
        }
        return result;
    },
    _add_comment: function(comment_data){
        if (this.comment_manager && comment_data.parent_object.pk == this.id){
            this.comment_manager.comments.push(new Comment(this.comment_manager, comment_data));
        } else {
            this.children.forEach(function(v){
                v._add_comment(comment_data);
            });
        }
    }
};
