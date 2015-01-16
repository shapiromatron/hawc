var dose_array = function(values){
  if (values){
    this._load_from_jsonify(values);
  } else {
    this._new_instance();
  }
  this.rebuild_table();
};

dose_array.prototype.jsonify = function(){
  this._update_array_values();
  var vals = [];
  for(var i=0; i<this.rows; i++){
    for(var j=0; j<this.columns; j++){
      vals.push({'dose_units': this.dose_units[j],
                 'dose_group_id': i,
                 'dose': parseFloat(this.array[i].doses[j])});
    }
  }
  return vals;
};

dose_array.prototype.add_dose_column = function(){
  this._update_array_values();
  this.columns += 1;
  this.dose_units.push("");
  for(var i=0; i<this.rows; i++){
    this.array[i].doses.push("");
  }
  this.rebuild_table();
};

dose_array.prototype.remove_dose_column = function(index){
  this._update_array_values();
  this.dose_units.splice(index, 1);
  for(var i=0; i<this.rows; i++){
    this.array[i].doses.splice(index,1);
  }
  this.columns -= 1;
  this.rebuild_table();
};

dose_array.prototype.change_rows = function(){
  this._update_array_values();
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
    this.rebuild_table();
  }
};

dose_array.prototype.rebuild_table = function(){
  this._build_colgroup();
  this._build_thead();
  this._build_tbody();
};

dose_array.prototype._update_array_values = function(){
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
};

dose_array.prototype._add_blank_row = function(cols){
  var set = {'doses': []};
  for(var j=0; j<cols; j++){
    set.doses.push("");
  }
  return set;
};

dose_array.prototype._build_thead = function(){
  var tr = $('<tr></tr>');
  tr.append('<th>Dose Units</th>');
  for(var j=0; j<this.columns; j++){
    var th = $('<th></th>');
    var select = $('<select class="input-medium dose_types"></select>');
    window.dose_types.forEach(function(v, i){
      select.append('<option value="' + v.id + '">' + v.units + '</option>');
    });
    if (this.dose_units[j]){
      select.find('option[value=' + this.dose_units[j] + ']').prop('selected', true);
    }
    th.append(select);
    if (j>0){
      th.append('<a href="#" class="remove_dose"> <i class="icon-remove-circle"></i></a>');
    }
    tr.append(th);
  }
  $('#dose_table thead').html(tr);
};

dose_array.prototype._build_colgroup = function(){
  var cols = [];
  cols.push('<col style="width:10%"></col>');
  for(var j=0; j<this.columns; j++){
    cols.push('<col style="width:' + (90/this.columns) +'%"></col>');
  }
  $('#dose_table colgroup').html(cols.join(""));
};

dose_array.prototype._build_tbody = function(){
  var tbody = $('#dose_table tbody').html("");
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
};

dose_array.prototype._get_number_dose_groups = function(){
  return parseInt($('#id_num_dose_groups').val());
};

dose_array.prototype._load_from_jsonify = function(values){
  var rows = 0,
      columns = 0,
      doses_hash = {},
      dose_units = [],
      array = [];

  // first pass for dimensions
  values.forEach(function(v, i){
    if (v.dose_group_id+1 > rows){
      rows = v.dose_group_id+1;
    }
    if (doses_hash[v.dose_units] === undefined){
        doses_hash[v.dose_units] = columns;
        dose_units.push(v.dose_units);
        columns += 1;
      }
  });

  //now build array
  for(var i=0; i<rows; i++){
    array.push(this._add_blank_row(columns));
  }

  // now fill-in array
  values.forEach(function(v, i){
    if (isFinite(parseFloat(v.dose))){
      array[v.dose_group_id].doses[doses_hash[v.dose_units]] = parseFloat(v.dose);
    }
  });

  this.rows = rows;
  this.columns = columns;
  this.array = array;
  this.dose_units= dose_units;
};

dose_array.prototype._new_instance = function(){
    var columns = 1,
      rows = this._get_number_dose_groups(),
      array = [];

    for(var i=0; i<rows; i++){
      array.push(this._add_blank_row(columns));
    }
    this.rows = rows;
    this.columns = columns;
    this.array = array;
    this.dose_units = [""];
};
