(function(wysihtml5, jQuery, SmartTag) {
    var dom = wysihtml5.dom;
    wysihtml5.commands.createSmartTag = {
        exec: function(composer, command, values) {

            var doc = composer.doc,
                anchor,
                textNode,
                node_name = (values.display_type === "popup") ? "SPAN" : "DIV",
                textContent = (values.display_type === "popup") ? values.title : values.caption;

            // create element
            anchor = doc.createElement(node_name);
            dom.setTextContent(anchor, textContent);
            anchor.setAttribute("data-type", values.resource);
            anchor.setAttribute("data-name", values.name);
            anchor.setAttribute("data-pk", values.pk);
            anchor.setAttribute("class", "smart-tag active");

            // clear existing
            if(values.existing){
                composer.selection.selectNode(values.existing);
                values.existing.remove();
            }

            // insert new element
            if (node_name === "SPAN"){
                textNode = doc.createTextNode(wysihtml5.INVISIBLE_SPACE);
                composer.selection.insertNode(textNode);
                composer.selection.setBefore(textNode);
                composer.selection.insertNode(anchor);
                composer.selection.setAfter(textNode);
            } else {
                composer.selection.insertNode(anchor);
            }

            SmartTag.initialize_tags($(composer.doc));
        }
    };

    $.fn.wysihtml5.Constructor.prototype.initInsertSmartTag = function(toolbar, modal) {
        var self = this,
            caretBookmark,
            values,
            getExistingTag = function() {
                var $node = $(editor.composer.selection.getSelection().anchorNode);
                return SmartTag.getExistingTag($node);
            }, insertSmartTag = function(e) {
                if (!isValid()) return e.stopPropagation();
                self.editor.currentView.element.focus();
                if (caretBookmark) {
                  self.editor.composer.selection.setBookmark(caretBookmark);
                  caretBookmark = null;
                }
                self.editor.composer.commands.exec("createSmartTag", values);
                modal.modal('hide');
            }, setValues = function(){
                var resourceName = modal.find("#id_resource").val();
                values = {
                    "resource": resourceName,
                    "name": $('#id_{0}_0'.printf(resourceName)).val(),
                    "pk": $('#id_{0}_1'.printf(resourceName)).val(),
                    "display_type": modal.find('#id_display_type').val(),
                    "title": modal.find("#id_title").val(),
                    "caption": modal.find("#id_caption").val(),
                    "existing": getExistingTag()
                }
            }, isValid = function(){
                var errs = [];
                setValues();

                if(values.name.length === 0 || values.pk.length === 0){
                    errs.push("<li>A resource must be selected (make sure to select one from the autopopulated menu).</li>");
                }
                if(values.display_type === "popup" && values.title.length === 0){
                    errs.push("<li>A title is required</li>");
                }
                if(values.display_type === "inline" && values.caption.length === 0){
                    errs.push("<li>A caption is required</li>");
                }

                modal.find(".errors").remove();
                if(errs.length>0){
                    $('<div class="errors alert alert-danger">')
                        .append($('<ul>').html(errs))
                        .appendTo(modal.find('.modal-body'));
                }

                return errs.length===0;
            }, modalStartup = function(){
                setInputsFromExisting(getExistingTag());
                modal.find('#id_resource').focus();
            }, setEditorFocus = function(){
                self.editor.currentView.element.focus();
            }, stopProp = function(e){
                e.stopPropagation();
            }, setInputsFromExisting = function(node){
                if(node){
                    var resourceName = node.dataset.type;
                    modal.find("#id_resource").val(resourceName).trigger('change');
                    modal.find('#id_{0}_0'.printf(resourceName)).val(node.dataset.name);
                    modal.find('#id_{0}_1'.printf(resourceName)).val(node.dataset.pk);
                    if(node.nodeName==="SPAN"){
                        modal.find('#id_display_type').val('popup').trigger('change');
                        modal.find('#id_title').val(node.textContent);
                    } else {
                        modal.find('#id_display_type').val('inline').trigger('change');
                        modal.find('#id_caption').val(node.textContent);
                    }
                } else {
                    modal.find('.smartTagSearch').val("");
                    modal.find('#id_title').val("");
                    modal.find('#id_caption').val("");
                }
            };

        modal.find('#id_resource').on('change', function(){
            modal.find('.smartTagSearch').parent().parent().hide();
            modal.find("#div_id_resource, #div_id_{0}".printf(this.value)).show();
        }).trigger('change');

        modal.find('#id_display_type').on('change', function(){
            if(this.value==="popup"){
                modal.find("#div_id_title").show();
                modal.find("#div_id_caption").hide();
            } else {
                modal.find("#div_id_title").hide();
                modal.find("#div_id_caption").show();
            }
        }).trigger('change');

        modal.on('click', '.smartTagSave', insertSmartTag)
            .on('show', modalStartup)
            .on('hide', setEditorFocus)
            .on('click.dismiss.modal', '[data-dismiss="modal"]', stopProp);

        toolbar.find('a[data-wysihtml5-command=insertSmartTag]').click(function() {
            var activeButton = $(this).hasClass("wysihtml5-command-active");
            if (!activeButton) {
                self.editor.currentView.element.focus(false);
                caretBookmark = self.editor.composer.selection.getBookmark();
                modal.modal('show');
                return false;
            }
            else {
                return true;
            }
        });
    };
})(wysihtml5, jQuery, SmartTag);
