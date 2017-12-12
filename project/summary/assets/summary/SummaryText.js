import $ from '$';

class SummaryText {
    constructor(obj, depth, tree, sibling_id, parent) {
        this.parent = parent;
        this.tree = tree;
        this.depth = depth;
        this.id = obj.id;
        this.data = obj.data;
        this.section_label = parent
            ? this.parent.section_label + (sibling_id + 1).toString() + '.'
            : '';

        var self = this,
            children = [];
        if (obj.children) {
            obj.children.forEach(function(child, i) {
                children.push(new SummaryText(child, depth + 1, tree, i, self));
            });
        }
        this.children = children;
    }

    static update_url(id) {
        return '/summary/{0}/update/'.printf(id);
    }
    static delete_url(id) {
        return '/summary/{0}/delete/'.printf(id);
    }

    static assessment_list_url(assessment_id) {
        return '/summary/assessment/{0}/summaries/json/'.printf(assessment_id);
    }

    get_option_item(lst) {
        var title = this.depth === 1 ? '(document root)' : this.data.title;
        lst.push(
            $(
                '<option value="{0}">{1}{2}</option>'.printf(
                    this.id,
                    Array(this.depth).join('&nbsp;&nbsp;'),
                    title
                )
            ).data('d', this)
        );
        this.children.forEach(function(v) {
            v.get_option_item(lst);
        });
    }

    get_children_option_items(lst) {
        this.children.forEach(function(v) {
            lst.push(
                '<option value="{0}">{1}</option>'.printf(v.id, v.data.title)
            );
        });
    }

    render_tree(lst) {
        lst.push(
            $(
                '<p class="summary_toc">{0}{1}</p>'.printf(
                    this.get_tab_depth(),
                    this.data.title
                )
            ).data('d', this)
        );
        this.children.forEach(function(v) {
            v.render_tree(lst);
        });
    }

    get_tab_depth() {
        return Array(this.depth - 1).join('&nbsp;&nbsp;');
    }

    print_section() {
        var div = $('<div id="{0}"></div>'.printf(this.data.slug)),
            header = $(
                '<h{0}>{1} {2}</h{3}>'.printf(
                    this.depth,
                    this.section_label,
                    this.data.title,
                    this.depth
                )
            ),
            content = $('<div>{0}</div>'.printf(this.data.text));

        return div.append(header, content);
    }

    render_header(lst) {
        lst.push(
            '<li><a href="#{0}">{1}{2} {3}<i class="icon-chevron-right"></i></a></li>'.printf(
                this.data.slug,
                this.get_tab_depth(),
                this.section_label,
                this.data.title
            )
        );
        this.children.forEach(function(v) {
            v.render_header(lst);
        });
    }

    render_body(lst) {
        lst.push(this.print_section());
        this.children.forEach(function(v) {
            v.render_body(lst);
        });
    }

    get_prior_sibling_id() {
        var self = this,
            result = -1;

        if (this.parent) {
            this.parent.children.forEach(function(v, i) {
                if (v.id === self.id && i > 0) {
                    result = self.parent.children[i - 1].id;
                }
            });
        }
        return result;
    }
}

export default SummaryText;
