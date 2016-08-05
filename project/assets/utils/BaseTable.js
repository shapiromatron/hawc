import TableFootnotes from './TableFootnotes';

// General object for creating any table
class BaseTable {

    constructor(){
        this.tbl = $('<table class="table table-condensed table-striped">');
        this.thead = $('<thead>');
        this.colgroup = $('<colgroup>');
        this.tbody = $('<tbody>');
        this.tfoot = $('<tfoot>');
        this.footnotes  = new TableFootnotes();
        this.tbl.append(this.colgroup, this.thead, this.tfoot, this.tbody);
    }

    getTbl(){
        this._set_footnotes();
        return this.tbl;
    }

    numCols(cols){
        if(cols){
            this._numCols = cols;
        } else if(this._numCols === undefined){
            this._numCols = d3.sum(_.map(
               this.thead.first().children().first().children(),
               function(d){return parseInt($(d).attr('colspan'))||1;}));
        }
        return this._numCols;
    }

    addHeaderRow(val){
        this.addRow(val, true);
    }

    addRow(val, isHeader){
        var tr,
            tagName = (isHeader) ? '<th>' : '<td>';
        if(val instanceof Array){
            tr = $('<tr>');
            val.forEach(function(v){tr.append($(tagName).html(v));});
        } else if (val instanceof jQuery && val.first().prop('tagName') === 'TR') {
            tr = val;
        } else {
            console.log('unknown input type');
        }
        if(isHeader){
            this.thead.append(tr);
        } else {
            this.tbody.append(tr);
        }
        return tr;
    }

    setColGroup(percents){
        this.colgroup.html(percents.map(function(v){
            return '<col style="width: {0}%;">'.printf(v);
        }));
    }

    _set_footnotes(){
        var txt = this.footnotes.html_list().join('<br>'),
            colspan = this.numCols();
        if (txt.length>0)
            this.tfoot.html('<tr><td colspan="{0}">{1}</td></tr>'.printf(colspan, txt));
    }
}

export default BaseTable;
