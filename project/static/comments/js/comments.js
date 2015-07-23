var CommentManager = function($el, data, object){
    this.$el = $el;
    this.object = object;
    this.data = data;
    this.object_type = data.object_type;
    this.object_id = data.object_id;
    this.user = data.user;
    this.comments = [];
    if(data.commenting_public && this.$el !== null){
        this.get_comments($.proxy(this.render, this));
    }
}
_.extend(CommentManager, {
    content_types: [
        "SummaryText", "ReferenceValue", "Assessment", "Study",
        "Experiment", "AnimalGroup", "Endpoint"
    ]
});
CommentManager.prototype = {
    render: function(){
        this.$el.html(this._display_comments());
        if (this.data.commenting_enabled){
            this.$el.append(this._create_comment_form());
        }
    },
    get_comments: function(cb){
        var self = this;
        this.$el.html('<p>Fetching comments... <img src="/static/img/loading.gif"></p>');
        $.get('/comments/{0}/{1}/'.printf(this.object_type, this.object_id), function(d){
            self.comments = _.map(d, function(v){return new Comment(self, v)});
            if (cb) cb();
        });
    },
    _display_comments: function(){
        return (this.data.displayAsTable) ? this._build_comment_table() : this._build_comment_list();
    },
    _build_comment_list: function(){
        var lead, lst;
        switch(this.comments.length){
            case 0:
                lead = "No one has commented yet";
                break;
            case 1:
                lead = "1 comment";
                break;
            default:
                lead = "{0} comments".printf(this.comments.length);
        }
        lst = this.comments.map(function(v){return v.display_html();});
        lst.unshift('<p class="lead">{0}</p>'.printf(lead));
        return lst;
    },
    _create_comment_form: function(){
        var content = ['<legend>Post a comment</legend>'];
        if(this.user<0){
            content.push('<p class="muted">You must be logged-in to submit a comment</p>');
        } else {
            var self = this,
                form = $('<form>'),
                title_input = $('<input placeholder="Comment title" class="span12"></input>'),
                text_input = $('<textarea rows="6" placeholder="Comment text" class="span12"></textarea>'),
                submit = $('<a class="btn btn-primary">Submit</a>').on('click', function(){
                    var url = '/comments/{0}/{1}/post/'.printf(self.object_type, self.object_id),
                        data = {"title": title_input.val(), "text": text_input.val()};
                    $.post(url, data, function(d){
                        clear_form_errors();
                        if (d.status==="fail"){
                            add_form_errors(d.details);
                        } else {
                            clear_form();
                            self.get_comments($.proxy(self.render, self));
                        }
                  });
                }),
                clear_form = function(){
                    form.find('input, textarea').val("");
                },
                clear_form_errors = function(){
                    $('.comment_form_errors').remove();
                },
                add_form_errors = function(errors){
                    var form_errors = $('<p class="comment_form_errors alert alert-error"></p>');
                    if(errors.title) form_errors.append('Title: ' + errors.title + '<br>');
                    if(errors.text) form_errors.append('Text: ' + errors.text + '<br>');
                    submit.before(form_errors);
                };
            content.push(title_input, '<br>', text_input, '<br>', submit);
        }
        return form.html(content);
    },
    _build_comment_table: function(){
        var tbl = $('<table class="table table-condensed  table-striped"></table>'),
            thead = $('<thead>'),
            tbody = $('<tbody>'),
            colgroup = $('<colgroup>')
                .append('<col style="width:25%;">')
                .append('<col style="width:60%;">')
                .append('<col style="width:15%;">');

        $('<tr>')
            .append('<th>Object</th>')
            .append('<th>Comment</th>')
            .append('<th>Commenter</th>')
            .appendTo(thead);

        _.each(CommentManager.content_types, function(ct){
            _.chain(this.comments)
                .filter(function(v){return v.data.parent_object.type === ct;})
                .each(function(v){tbody.append(v.build_table_row());});
        }, this);

        return tbl.append(colgroup, thead, tbody);
    },
    add_popup_button: function($obj){
        var title;
        switch(this.comments.length){
            case 0:
                title = "Comment";
                break;
            case 1:
                title = "1 comment";
                break;
            default:
                title = "{0} comments".printf(this.comments.length);
        }

        $('<a class="btn btn-mini pull-right">')
            .text(title)
            .click($.proxy(this.display_comments, this))
            .appendTo($obj);
    },
    display_comments: function(){
        var modal = new HAWCModal(),
            title = 'Comments for {0}'.printf(this.object.data.title),
            content;

        this.$el = modal.getBody();

        if(this.data.commenting_public){
            content = this._build_comment_list();
        } else {
            content = [];
        }

        if(this.data.commenting_enabled){
            content.push(this._create_comment_form());
        }

        modal.addHeader(title)
            .addBody($('<div class="row-fluid">').html(content))
            .addFooter("")
            .show({maxWidth: 800});

    }
};


var Comment = function(manager, data){
    this.manager = manager;
    this.data = data;
    this.data.created = new Date(this.data.created);
    this.data.last_updated = new Date(this.data.last_updated);
};
Comment.prototype = {
    display_html: function(){
        var head = $('<p>').html('<b>{0}</b><span class="muted"> | {1}</span>'.printf(
                this.data.commenter,
                this.data.last_updated.toDateString())
            ),
            title = $('<p>').html('<b><i>{0}</i></b>'.printf(this.data.title)),
            content = $('<p>').html(this.data.text);

        if (this.data.commenter_pk === this.manager.user){
            head.append(
                $('<a class="btn btn-small btn-danger pull-right" title="Delete your comment"><b>x</b></a>')
                        .on('click', $.proxy(this.delete, this)));
        }
        return $('<div>').append(head, title, content, '<hr>');
    },
    delete: function(){
        var mgr = this.manager,
            url = '/comments/{0}/delete/'.printf(this.data.pk);
        $.post(url, function(d){
            if(d.status==="success") mgr.get_comments($.proxy(mgr.render, mgr));
        });
    },
    build_table_row: function(){
        return $('<tr>').append([
            '<td><a href="{0}">{1}</a><p class="muted">{2}</p></td>'.printf(
                this.data.parent_object.url, this.data.parent_object.name, this.data.parent_object.type),
            '<td><b>{0}</b><br><p>{1}</p></td>'.printf(
                this.data.title, this.data.text),
            '<td><b>{0}</b><br><p class="muted">{1}</p></td>'.printf(
                this.data.commenter, this.data.last_updated)
        ]);
    }
};
