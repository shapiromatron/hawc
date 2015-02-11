var DosingRegimeForm = function(form, dose_types, initial){
  this.form = form;
  this.dose_types = dose_types;
  this._setInitialValues(initial);
  this.rebuildTable();
  this._setEventHandlers();
};

DosingRegimeForm.prototype  = {
  _setInitialValues: function(initial){
    var rows = 0,
        columns = 0,
        dose_units = [],
        doses_hash = {},
        array = [];

    if (initial){
      //unpack data from JSON file
      initial.forEach(function(v, i){
        if (v.dose_group_id+1 > rows){
          rows = v.dose_group_id+1;
        }
        if (doses_hash[v.dose_units] === undefined){
            doses_hash[v.dose_units] = columns;
            dose_units.push(v.dose_units);
            columns += 1;
          }
      });

      // build array
      for(var i=0; i<rows; i++){
        array.push(this._add_blank_row(columns));
      }

      // fill-in array
      initial.forEach(function(v, i){
        if (isFinite(parseFloat(v.dose))){
          array[v.dose_group_id].doses[doses_hash[v.dose_units]] = parseFloat(v.dose);
        }
      });

    } else {
      rows = this._get_number_dose_groups();
      columns = 1;
      dose_units.push("");
      array = [];
      for(var i=0; i<rows; i++){
        array.push(this._add_blank_row(columns));
      }
    }

    this.rows = rows;
    this.columns = columns;
    this.array = array;
    this.dose_units = dose_units;

    this.rebuildTable();
  }, jsonify: function(){
    this._syncFromForm();
    var vals = [];
    for(var i=0; i<this.rows; i++){
      for(var j=0; j<this.columns; j++){
        vals.push({'dose_units': this.dose_units[j],
                   'dose_group_id': i,
                   'dose': parseFloat(this.array[i].doses[j])});
      }
    }
    return vals;
  }, add_dose_column: function(){
    this._syncFromForm();
    this.columns += 1;
    this.dose_units.push("");
    for(var i=0; i<this.rows; i++){
      this.array[i].doses.push("");
    }
    this.rebuildTable();
  }, remove_dose_column: function(index){
    this._syncFromForm();
    this.dose_units.splice(index, 1);
    for(var i=0; i<this.rows; i++){
      this.array[i].doses.splice(index,1);
    }
    this.columns -= 1;
    this.rebuildTable();
  }, change_rows: function(){
    this._syncFromForm();
    var new_rows = this._get_number_dose_groups();
    if (new_rows !== this.rows){
      var new_array = [];
      for(var i=0; i<new_rows; i++){
        if (this.array[i]){
          new_array.push(this.array[i]);
        } else {
          new_array.push(this._add_blank_row(this.columns));
        }
      }
      this.array = new_array;
      this.rows = new_rows;
      this.rebuildTable();
    }
  }, rebuildTable: function(){
    $('#dose_table')
      .html("")
      .append(
        this._build_colgroup(),
        this._build_thead(),
        this._build_tbody()
      );
  }, _syncFromForm: function(){
    // rebuild dose-units and dose-array values from form
    var self = this;

    this.dose_units =  [];
    $('#dose_table thead th select option:selected').each(function(i, v){
      self.dose_units.push(parseFloat(this.value));
    });

    $('#dose_table tbody tr').each(function(i1, v1){
      $(v1).find('td input').each(function(i2, v2){
        self.array[i1].doses[i2] = $(v2).val();
      });
    });
  }, _add_blank_row: function(numCols){
      var doses = [];
      for(var j=0; j<numCols; j++)
        doses.push("");
      return {"doses": doses}
  }, _build_thead: function(){
    var tr = $('<tr>').append('<th>Dose Units</th>');
    for(var j=0; j<this.columns; j++){
      var th = $('<th>');
      var select = $('<select class="input-medium dose_types"></select>');
      this.dose_types.forEach(function(v, i){
        select.append('<option value="{0}">{1}</option>'.printf(v.id, v.units));
      });
      if (this.dose_units[j]){
        select.find('option[value={0}]'.printf(this.dose_units[j])).prop('selected', true);
      }
      th.append(select);
      if (j>0){
        th.append('<a href="#" class="remove_dose"> <i class="icon-remove-circle"></i></a>');
      }
      tr.append(th);
    }
    return $('<thead>').html(tr);
  }, _build_colgroup: function(){
    var cols = [];
    cols.push('<col style="width:10%"></col>');
    for(var j=0; j<this.columns; j++){
      cols.push('<col style="width:' + (90/this.columns) +'%"></col>');
    }
    return $('<colgroup>').html(cols.join(""));
  }, _build_tbody: function(){
    var tbody = $('<tbody>');
    for(var i=0; i<this.rows; i++){
      var tr = $('<tr></tr>');
      tr.append('<td><label class="control-label">Dose Group {0}</label></td>'
            .printf(i+1));
      for(var j=0; j<this.columns; j++){
        tr.append('<td><input type="text" tabindex="{0}" class="input-medium" id="dose_{1}" value="{2}"></td>'
            .printf(j+1, i, this.array[i].doses[j]));
      }
      tbody.append(tr);
    }
    return tbody;
  }, _get_number_dose_groups: function(){
    return Math.min(parseInt(this.form.find('#id_num_dose_groups').val()), 20);
  },
  _setEventHandlers: function(){
    var self = this;

    this.form.find('#id_description').wysihtml5({"stylesheets": false});

    this.form.find('#id_num_dose_groups').on('change', function(){
      self.change_rows();
    });

    this.form.find('#new_dose_column').on('click', function(){
      event.preventDefault();
      self.add_dose_column();
    });

    $('#dose_table').on('click', '.remove_dose', function(e){
      e.preventDefault();
      var td_index = $(this).parent().index()-1;
      self.remove_dose_column(td_index);
    });

    this.form.submit(function(){
      self.form.find('#dose_groups_json').val(JSON.stringify(self.jsonify()));
      return true;
    });

  }
};
