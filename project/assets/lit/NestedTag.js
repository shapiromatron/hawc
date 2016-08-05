import $ from '$';

import Observee from 'utils/Observee';

import Reference from './Reference';


class NestedTag extends Observee {

    constructor(item, level, tree, parent){
        super();
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
    }

    get_nested_list_item(parent, padding, options){
        var div = $('<div data-id="{0}">'.printf(this.data.pk)),
            collapse = $('<span class="nestedTagCollapser"></span>').appendTo(div),
            txtspan = $('<p class="nestedTag"></p>'),
            text = '{0}{1}'.printf(padding, this.data.name);

        if(options && options.show_refs_count) text += ' ({0})'.printf(this.data.reference_count);
        txtspan.text(text)
               .appendTo(div)
               .data('d', this)
               .on('click', function(){$(this).trigger('hawc-tagClicked');});
        parent.append(div);

        if(this.children.length>0){
            var toggle = $('<a>')
                .attr('title', 'Collapse tags: {0}'.printf(this.data.name))
                .attr('data-toggle', 'collapse')
                .attr('href', '#collapseTag{0}'.printf(this.data.pk))
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
            this.children.forEach(function(v){v.get_nested_list_item(nested, padding + '   ', options);});
            if (options && options.sortable){
                nested.sortable({
                    containment: parent,
                    start(event, ui) {
                        var start_pos = ui.item.index();
                        ui.item.data('start_pos', start_pos);
                    },
                    stop(event, ui) {
                        var start_pos = ui.item.data('start_pos'),
                            offset = ui.item.index() - start_pos;
                        if (offset !== 0) $(this).trigger('hawc-tagMoved', [ui.item, offset]);
                    },
                });
            }
        }

        return parent;
    }

    get_reference_objects_by_tag(reference_viewer){
        var url = '/lit/assessment/{0}/references/{1}/json/'
            .printf(window.assessment_pk, this.data.pk);
        if (window.search_id) url += '?search_id={0}'.printf(window.search_id);

        $.get(url, function(results){
            if(results.status=='success'){
                var refs = [];
                results.refs.forEach(function(datum){refs.push(new Reference(datum, window.tagtree));});
                reference_viewer.set_references(refs);
            } else {
                reference_viewer.set_error();
            }
        });
    }

    get_option_item(lst){
        lst.push($('<option value="{0}">{1}{2}</option>'
                    .printf(this.data.pk, Array(this.level+1).join('&nbsp;&nbsp;'), this.data.name))
                    .data('d', this));
        this.children.forEach(function(v){v.get_option_item(lst);});
        return lst;
    }

    _append_to_dict(dict){
        dict[this.data.pk] = this;
        this.children.forEach(function(v){v._append_to_dict(dict);});
    }

    get_full_name(){
        if(this.parent && this.parent.get_full_name){
            return this.parent.get_full_name() + ' ➤ ' + this.data.name;
        } else {
            return this.data.name;
        }
    }

    add_child(name){
        var self = this,
            data = {
                'status': 'add',
                'parent_pk': this.data.pk,
                name,
            };

        $.post('.', data, function(v){
            if (v.status === 'success'){
                self.children.push(new NestedTag(v.node[0], self.level+1, self.tree, self));
                self.tree.tree_changed();
            }
        });
    }

    remove_self(){
        this.children.forEach(function(v){v.remove_self();});
        var self = this,
            data = {
                'status': 'remove',
                'pk': this.data.pk,
            };

        $.post('.', data, function(v){
            if (v.status === 'success'){
                self.notifyObservers({'event': 'tag removed', 'object': self});
                if(self.parent){
                    self.parent.remove_child(self);
                } else {
                    self.tree.remove_child(self);
                }
                self.tree.tree_changed();
            }
        });
    }

    move_self(offset){
        var self = this,
            lst = this.parent.children,
            index = lst.indexOf(this),
            data = {
                'status': 'move',
                'pk': this.data.pk,
                offset,
            };

        // update locally
        lst.splice(index+offset, 0, lst.splice(index, 1)[0]);

        $.post('.', data, function(v){
            if (v.status === 'success') self.tree.tree_changed();
        });
    }

    rename_self(name){
        var self = this,
            data = {
                'status': 'rename',
                'pk': this.data.pk,
                name,
            };

        $.post('.', data, function(v){
            if (v.status === 'success'){
                self.data.name = name;
                self.tree.tree_changed();
            }
        });
    }

    remove_child(tag){
        this.children.splice_object(tag);
    }
}

export default NestedTag;
