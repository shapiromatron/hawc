var CommentManager = function(data, object){
    this.object = object;
    this.data = data;
    this.object_type = data.object_type;
    this.object_id = data.object_id;
    this.user = data.user;
    this.$div = $(data.comment_div_selector);
    this.comments = [];
    this.$comments = $('<div></div>');
    this.$comments_form = $('<form></form>');
    this.$div.html([this.$comments, this.$comments_form]);
    if((data.commenting_public) && (data.fetch_comments)) this.get_comments();
    if((data.commenting_enabled) && (data.fetch_comments)) this.insert_inline_comment_form();
};

CommentManager.content_types = ["SummaryText", "ReferenceValue", "Assessment", "Study",
                                "Aggregation", "Experiment", "AnimalGroup",
                                "Endpoint"];

CommentManager.prototype.get_comments = function(){
  var self = this;
  this.$comments.html('<p>Fetching comments... <img src="/static/img/loading.gif"></p>');
  $.get('/comments/{0}/{1}/'.printf(this.object_type, this.object_id), function(d){
      self.comments = []; // reset
      d.forEach(function(v){self.comments.push(new Comment(self, v));});
      self._display_comments(self.$comments);
  });
};

CommentManager.prototype._display_comments = function($div){
  var content = [];
  if(this.comments.length === 0){
    content.push('<p class="muted">No one has commented yet.</p><hr>');
  } else {
    if (cm.object_type == "assessment_all"){
      content.push(this._comments_summary_table());
    } else {
      this._build_comment_list(content);
    }
  }
  $div.html(content);
};

CommentManager.prototype._build_comment_list = function(lst){
  var comment_plurality = (this.comments.length===1) ? "comment" : "comments";
      lst.push('<hr><p class="lead">{0} {1}</p>'.printf(this.comments.length,
                                                        comment_plurality));
  this.comments.forEach(function(v){
    lst.push(v.display_html());
  });
};

CommentManager.prototype._create_comment_form = function($form){
  var content = ['<legend>Post a comment</legend>'];
  if(this.user<0){
    content.push('<p class="muted">You must be logged-in to submit a comment</p>');
  } else {
    var self = this,
        title_input = $('<input placeholder="  Comment title" class="span12"></input>'),
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
              self.get_comments();
            }
          });
        }),
        clear_form = function(){
          self.$comments_form.find('input, textarea').val("");
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
    content.push(title_input, '<br>',
                 text_input, '<br>',
                 submit);
  }
  $form.html(content);
};

CommentManager.prototype.insert_inline_comment_form = function(){
  this._create_comment_form(this.$comments_form);
};

CommentManager.prototype._comments_summary_table = function(){
  // build a summary-table version of a comment
  var self = this,
      build_tr  = function(list, field_type){
        var tr = $('<tr></tr');
        list.forEach(function(v){
          tr.append($('<{0}></{0}>'.printf(field_type)).append(v));
        });
        return tr;
      },
      tbl = $('<table class="table table-condensed  table-striped"></table>'),
      thead = $('<thead></thead>'),
      tbody = $('<tbody></tbody>');
      colgroup = $('<colgroup></colgroup>').append('<col style="width:25%;">')
                                           .append('<col style="width:60%;">')
                                           .append('<col style="width:15%;">');

  tbl.append(colgroup, thead, tbody);
  thead.append(build_tr(['Object', 'Comment', 'Commenter'], 'th'));

  CommentManager.content_types.forEach(function(content_type){
    var comments = self.comments.filter(function(v){
      return v.data.parent_object.type === content_type;
    });
    comments.forEach(function(v){
      tbody.append(build_tr(v.build_table_row(), 'td'));
    });
  });
  return tbl;
};

CommentManager.prototype.build_popup_button = function($obj){

  var self = this,
      txt = 'Comment';
  if(this.comments.length == 1){
    txt='1 Comment';
  } else if (this.comments.length>1){
    txt = '{0} Comments'.printf(this.comments.length);
  }

  var a = $('<a class="btn btn-mini pull-right">{0}</a>'.printf(txt))
              .on('click', function(e){self.build_popup_form(self, e);});
    $obj.append(a);
};

CommentManager.prototype.build_popup_form = function(){
  this.tooltip = new PlotTooltip({"width": "700px", "height": "450px"});
  this.tooltip.display_comments(this, event);
};


var Comment = function(manager, data){
  this.manager = manager;
  this.data = data;
  this.data.created = new Date(this.data.created);
  this.data.last_updated = new Date(this.data.last_updated);
};

Comment.prototype.display_html = function(){
  var self = this,
      head = $('<p></p>').html('<b>' + this.data.commenter +
                               '</b><span class="muted"> | ' +
                               this.data.last_updated.toDateString() + "</span>"),
      title = $('<p></p>').html('<b><i>{0}</i></b>'.printf(this.data.title)),
      content = $('<p></p>').html(this.data.text);

  if (this.data.commenter_pk === this.manager.user){
    head.append($('<a class="btn btn-small btn-danger pull-right" title="Delete your comment"><b>x</b></a>')
        .on('click', function(){self.delete();}));
  }
  return $('<div></div>').append(head, title, content, '<hr>');
};

Comment.prototype.delete = function(){
  var self = this,
      url = '/comments/{0}/delete/'.printf(this.data.pk);
  $.post(url, function(d){
    if(d.status==="success")self.manager.get_comments();
  });
};

Comment.prototype.build_table_row = function(){
  var contents = [];
  contents.push($('<a href="{0}">{1}</a><p class="muted">{2}</p>'.printf(this.data.parent_object.url,
                                                               this.data.parent_object.name,
                                                               this.data.parent_object.type)),
                $('<b>{0}</b><br><p>{1}</p>'.printf(this.data.title, this.data.text)),
                $('<b>{0}</b><br><p class="muted">{1}</p>'.printf(this.data.commenter,
                                                                  this.data.last_updated)));
  return contents;
};
