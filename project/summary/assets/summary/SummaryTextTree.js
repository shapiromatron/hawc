import $ from '$';
import _ from 'lodash';

import HAWCUtils from 'utils/HAWCUtils';

import SmartTagContainer from 'smartTags/SmartTagContainer';

import SummaryText from './SummaryText';

class SummaryTextTree {
    constructor(options) {
        this.options = options;
        this.root = undefined;
        this.get_summaries();
    }

    get_summaries() {
        var self = this,
            url = SummaryText.assessment_list_url(this.options.assessment_id);
        $.get(url, function(d) {
            self.root = new SummaryText(d[0], 1, self, 0);
            if (self.options.mode == 'read') {
                self._update_read();
            } else if (self.options.mode === 'modify') {
                self._update_modified();
            }
        });
    }

    _update_read() {
        this.render_docheaders();
        this.render_doctext();
        this.enable_affix();
        this._setSmartTags();
    }

    _update_modified() {
        this.options.update_textdiv.fadeOut();
        this.render_doctree();
        this.set_modify_events();
    }

    render_docheaders() {
        var contents = [],
            txt;
        if (this.root.children.length === 0) {
            txt = '<li><a href="#"><i>No summary-text is available.</i></a></li>';
            contents.push(txt);
        } else {
            _.each(this.root.children, function(d) {
                d.render_header(contents);
            });
        }
        this.options.read_headers_ul.html(contents);
    }

    render_doctext() {
        var contents = [];
        if (this.root.children.length === 0) {
            contents.push('<p>No summary-text is available.</p>');
        } else {
            this.root.children.forEach(function(v) {
                v.render_body(contents);
            });
        }
        this.options.read_text_div.html(contents);
    }

    update_textdiv(obj) {
        this.selected = obj;
        var self = this,
            isNew = obj === undefined,
            parent_options = function() {
                var lst = [],
                    select = self.options.update_textdiv.find('select#id_parent');
                self.root.get_option_item(lst);
                select.html(lst);
                if (!isNew) {
                    select.find('option[value="{0}"]'.printf(obj.parent.id)).prop('selected', true);
                }
            },
            sibling_options = function() {
                var select = self.options.update_textdiv.find('select#id_sibling'),
                    text_node_id = parseInt(
                        self.options.update_textdiv.find('select#id_parent option:selected').val(),
                        10
                    ),
                    lst = ['<option value="">(none)</option>'],
                    parent = self.get_summarytext_node(text_node_id);
                parent.get_children_option_items(lst);
                select.html(lst);
                if (!isNew) {
                    select
                        .find('option[value="{0}"]'.printf(obj.get_prior_sibling_id()))
                        .prop('selected', true);
                }
            },
            load_contents = function() {
                if (obj) {
                    self.options.update_textdiv.find('#id_title').val(obj.data.title);
                    self.options.update_textdiv.find('#id_slug').val(obj.data.slug);
                    self.options.text_editor.setContent(obj.data.text);
                    self.options.update_textdiv.find('#id_text').val(obj.data.text);
                } else {
                    self.options.update_textdiv.find('#id_title').val('');
                    self.options.update_textdiv.find('#id_slug').val('');
                    self.options.text_editor.setContent('');
                }
            },
            toggleEditOptions = function(isNew) {
                var sel = self.options.update_textdiv.find('#deleteSTBtn');
                isNew ? sel.hide() : sel.show();
            };

        load_contents();
        toggleEditOptions();
        parent_options();
        sibling_options();
        self.options.update_textdiv.fadeIn();
        self.options.update_textdiv.find('select#id_parent').on('change', function() {
            sibling_options(obj, isNew);
        });
    }

    set_modify_events() {
        var self = this;

        this.options.update_new.unbind().on('click', function() {
            self.update_textdiv();
        });

        this.options.update_textdiv
            .find('form')
            .unbind()
            .submit(function(e) {
                e.preventDefault();
                self.submit();
            });

        this.options.update_delete.unbind().on('click', function() {
            var url = SummaryText.delete_url(self.selected.id);
            $.post(url, self._redraw.bind(self));
        });

        this.options.update_doctree.unbind().on('click', '.summary_toc', function() {
            self.update_textdiv($(this).data('d'));
        });
    }

    render_doctree() {
        var contents = [];
        if (this.root.children.length === 0) {
            contents.push('<p><i>No contents.</i></p>');
        } else {
            this.root.children.forEach(function(v) {
                v.render_tree(contents);
            });
        }
        this.options.update_doctree.html(contents);
    }

    get_summarytext_node(id) {
        var node,
            get_id = function(st, id) {
                if (st.id === id) {
                    node = st;
                    return;
                }
                st.children.forEach(function(v) {
                    get_id(v, id);
                });
            };

        get_id(this.root, id);
        return node;
    }

    submit() {
        this.options.text_editor.prepareSubmission();
        var form = this.options.update_textdiv.find('form'),
            data = form.serialize(),
            url = '.';
        if (this.selected && this.selected.id) {
            url = SummaryText.update_url(this.selected.id);
        }
        $.post(url, data, this._redraw.bind(this));
        return false;
    }

    _redraw(res) {
        this.options.update_textdiv.find('.alert').remove();
        if (res.status == 'ok') {
            this.root = new SummaryText(res.content[0], 1, this);
            this._update_modified();
        } else {
            HAWCUtils.addAlert(res, this.options.update_textdiv);
        }
    }

    enable_affix() {
        $('.affix-sidenav a').click(function(e) {
            var href = $(this).attr('href'),
                offsetTop = href === '#' ? 0 : $(href).offset().top - 65;

            $('html, body')
                .stop()
                .animate({ scrollTop: offsetTop }, 300);
            e.preventDefault();
        });

        $('[data-spy="scroll"]').each(function() {
            $(this).scrollspy('refresh');
        });
    }

    _setSmartTags() {
        new SmartTagContainer(this.options.read_text_div, {
            showOnStartup: true,
        });
    }
}

export default SummaryTextTree;
