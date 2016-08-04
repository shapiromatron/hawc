class TableField extends InputField {

    constructor() {
        return InputField.apply(this, arguments);
    }

    renderHeader(){
        return HAWCUtils.abstractMethod();
    }

    addRow(){
        return HAWCUtils.abstractMethod();
    }

    fromSerializedRow(){
        return HAWCUtils.abstractMethod();
    }

    toSerializedRow(){
        return HAWCUtils.abstractMethod();
    }

    toSerialized() {
        this.parent.settings[this.schema.name] =
            _.chain(this.$tbody.children())
             .map(this.toSerializedRow, this)
             .compact()
             .value();
    }

    fromSerialized() {
        var arr = this.parent.settings[this.schema.name] || [];
        this.$tbody.empty();
        if (arr.length === 0 && this.schema.addBlankRowIfNone) {
            this.addRow();
        } else {
            _.each(arr, this.fromSerializedRow, this);
        }
    }

    setColgroup() {
        var cw = this.schema.colWidths || [],
            setCol = function(d){return '<col width="{0}%"'.printf(d);};
        $('<colgroup>')
            .append(_.map(cw, setCol))
            .appendTo(this.table);
    }

    render() {
        var $div = $('<div class="control-group form-row">');

        if (this.schema.prependSpacer) new SpacerNullField(this.schema, this.$parent).render();
        if (this.schema.label) new HeaderNullField(this.schema, this.$parent).render();
        if (this.schema.helpText) new HelpTextNullField(this.schema, this.$parent).render();

        this.table = $('<table class="table table-condensed table-bordered">').appendTo($div);
        this.setColgroup();
        this.$thead = $('<thead>').appendTo(this.table);
        this.$tbody = $('<tbody>').appendTo(this.table);
        this.renderHeader();
        $div.appendTo(this.$parent);
    }

    thOrdering(options) {
        var th = $('<th>').html('Ordering&nbsp;'),
            add = $('<button class="btn btn-mini btn-primary" title="Add row"><i class="icon-plus icon-white"></button>')
                    .on('click', this.addRow.bind(this));

        if (options.showNew) th.append(add);
        return th;
    }

    tdOrdering() {
        var moveUp = function(){
                var tr = $(this.parentNode.parentNode),
                    prev = tr.prev();
                if (prev.length>0) tr.insertBefore(prev);
            },
            moveDown = function(){
                var tr = $(this.parentNode.parentNode),
                    next = tr.next();
                if (next.length>0) tr.insertAfter(next);
            },
            del = function(){
                $(this.parentNode.parentNode).remove();
            },
            td = $('<td>');

        td.append(
            $('<button class="btn btn-mini" title="Move up"><i class="icon-arrow-up"></button>').on('click', moveUp),
            $('<button class="btn btn-mini" title="Move down"><i class="icon-arrow-down"></button>').on('click', moveDown),
            $('<button class="btn btn-mini" title="Remove"><i class="icon-remove"></button>').on('click', del)
        );
        return td;
    }

    addTdP(cls, txt){
        return $('<td>').append($('<p>').attr('class', cls).text(txt));
    }

    addTdText(name, val){
        val = val || '';
        return $('<td><input name="{0}" value="{1}" class="span12" type="text"></td>'.printf(name, val));
    }

    addTdInt(name, val){
        val = val || '';
        return '<td><input name="{0}" value="{1}" class="span12" type="number"></td>'.printf(name, val);
    }

    addTdFloat(name, val){
        val = val || '';
        return '<td><input name="{0}" value="{1}" class="span12" type="number" step="any"></td>'.printf(name, val);
    }

    addTdColor(name, val){
        val = val || '#000000';
        return $('<td>')
           .append($('<input type="color" name="{0}" value="{1}" class="span12" required>'.printf(name, val)));
    }

    addTdCheckbox(name, checked){
        let checkProp = (checked) ? 'checked': '';
        return $('<td>')
           .append($('<input type="checkbox" name="{0}" {1} required>'.printf(name, checkProp)));
    }

    addTdSelect(name, values){
        var sel = $('<select name="{0}" class="span12">'.printf(name))
                .append(_.map(values, function(d){return '<option value="{0}">{0}</option>'.printf(d);}));
        return $('<td>').append(sel);
    }

    addTdSelectLabels(name, options){
        var sel = $('<select name="{0}" class="span12">'.printf(name))
                .append(_.map(options, function(d){return '<option value="{0}">{1}</option>'.printf(
                        d.value, d.label);}));
        return $('<td>').append(sel);
    }

    addTdSelectMultiple(name, values){
        var sel = $('<select name="{0}" class="span12" multiple>'.printf(name))
                .append(_.map(values, function(d){return '<option value="{0}">{0}</option>'.printf(d);}));
        return $('<td>').append(sel);
    }
}


class ReferenceLineField extends TableField {

    constructor(){
        return TableField.apply(this, arguments);
    }

    renderHeader() {
        return $('<tr>')
            .append(
                '<th>Line value</th>',
                '<th>Caption</th>',
                '<th>Style</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    }

    addRow() {
        return $('<tr>')
            .append(
                this.addTdFloat('value'),
                this.addTdText('title'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.lines, 'name')),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    }

    fromSerializedRow(d,i) {
        var row = this.addRow();
        row.find('input[name="value"]').val(d.value);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            'value': parseFloat(row.find('input[name="value"]').val(), 10),
            'title': row.find('input[name="title"]').val(),
            'style': row.find('select[name="style"]').val(),
        };
    }

}

class ReferenceRangeField extends TableField {

    constructor(){
        return TableField.apply(this, arguments);
    }

    renderHeader(){
        return $('<tr>')
            .append(
                '<th>Lower value</th>',
                '<th>Upper value</th>',
                '<th>Caption</th>',
                '<th>Style</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    }

    addRow(){
        return $('<tr>')
            .append(
                this.addTdFloat('lower'),
                this.addTdFloat('upper'),
                this.addTdText('title'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.rectangles, 'name')),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    }

    fromSerializedRow(d,i){
        var row = this.addRow();
        row.find('input[name="lower"]').val(d.lower);
        row.find('input[name="upper"]').val(d.upper);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    }

    toSerializedRow(row){
        row = $(row);
        return {
            lower: parseFloat(row.find('input[name="lower"]').val(), 10),
            upper: parseFloat(row.find('input[name="upper"]').val(), 10),
            title: row.find('input[name="title"]').val(),
            style: row.find('select[name="style"]').val(),
        };
    }

}


class ReferenceLabelField extends TableField {

    constructor(){
        return TableField.apply(this, arguments);
    }

    renderHeader(){
        return $('<tr>')
            .append(
                '<th>Caption</th>',
                '<th>Style</th>',
                '<th>Max width (px)</th>',
                '<th>X position</th>',
                '<th>Y position</th>',
                this.thOrdering({showNew: true})
            ).appendTo(this.$thead);
    }

    addRow(){
        return $('<tr>')
            .append(
                this.addTdText('caption'),
                this.addTdSelect('style', _.pluck(D3Visualization.styles.texts, 'name')),
                this.addTdInt('max_width', 0),
                this.addTdInt('x', 0),
                this.addTdInt('y', 0),
                this.tdOrdering()
            ).appendTo(this.$tbody);
    }

    fromSerializedRow(d,i) {
        var row = this.addRow();
        row.find('input[name="caption"]').val(d.caption);
        row.find('select[name="style"]').val(d.style);
        row.find('input[name="max_width"]').val(d.max_width);
        row.find('input[name="x"]').val(d.x);
        row.find('input[name="y"]').val(d.y);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            caption:  row.find('input[name="caption"]').val(),
            style: row.find('select[name="style"]').val(),
            max_width: parseInt(row.find('input[name="max_width"]').val(), 10),
            x: parseInt(row.find('input[name="x"]').val(), 10),
            y: parseInt(row.find('input[name="y"]').val(), 10),
        };
    }

}


export {ReferenceLineField};
export {ReferenceRangeField};
export {ReferenceLabelField};
