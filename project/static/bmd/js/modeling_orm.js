// move to utility functions
function isInt(n) {
   return ((typeof n === 'number') && ((n % 1) === 0));
}

function isFloat(n) {
   return ((typeof n === 'number') && (!isNaN(n)));
}

// SESSION OBJECT
// ==============
// Parent Object
var Session = function(session, endpoint, logic_list, crud, bmds_version){
    this.session = session.session;
    this.session.sufficiently_close_BMDL = 3; // todo - move to bmd option in django, not hard-coded
    this.endpoint = endpoint;
    this.logic_list = new LogicList(this, logic_list);
    this.crud = crud;
    this.bmds_version = bmds_version;

    // add bmrs
    this.bmrs = [];
    for (var i=0;i<this.session.bmrs.length;i++){
        this.add_bmr(new BMR(session, session.session.bmrs[i]));
    }

    // add options and outputs
    this.option_files = [];
    this.outputs = [];
    if (this.crud=='Create'){
        for (i=0;i<session.models.length;i++){
            this.load_options_template(session.models[i]);
        }
    } else {
        for (i=0;i<session.models.length;i++){
            this.load_options_session(session.models[i]);
        }
    }
    this.print_options();
    this.print_bmrs();
    bmd_output_plot.build_plot();
    raw_output_img.build_plot();

    this.output_tbl = new OutputTable('#bmd_output_tbl', this);
    this.selection = new Selection(this);
    this.recommendation_table = new Tbl_Recommendation(this);
};

Session.prototype.add_bmr = function(bmr){
    this.bmrs.push(bmr);
};

Session.prototype.add_option = function(option, default_override){
    default_override = default_override || true;
    var opt = new OptionFile(this, option);
    this.option_files.push(opt);
    if (default_override){opt.default_overrides();}
    this.print_options();
};

Session.prototype.load_options_template = function(option){
    var opt = new OptionFile(this, option);
    opt.default_overrides();
    this.option_files.push(opt);
};

Session.prototype.load_options_session = function(option){
    var option_file, output;
    if (option.option_id >= this.outputs.length){
        option_file = new OptionFile(this, option);
        output = new BMDOutput(this, option, option_file, this.bmrs[option.bmr_id]);
        this.outputs.push([output]);
        this.option_files.push(option_file);
    } else {
        option_file = this.option_files[option.option_id];
        output = new BMDOutput(this, option, option_file, this.bmrs[option.bmr_id]);
        this.outputs[option.option_id].push(output);
    }
};

Session.prototype.print_options = function(){
    var bmd_tbl = $('#bmd_setup_tbl tbody').empty();
    this.option_files.forEach(function(v){
        bmd_tbl.append(v.option_summary_row());
    });
};

Session.prototype.print_bmrs = function(){
    var bmr_tbl = $('#bmr_setup_tbl tbody').empty();
    this.bmrs.forEach(function(v){
        bmr_tbl.append(v.option_summary_row());
    });
};

Session.prototype.submit_settings = function(){
    var d = {'options':[], 'bmrs':[],
             'dose_units_id': this.endpoint.data.doses[this.endpoint.data.dose_units_index].units_id};
    d.endpoint_id =  this.endpoint.data.pk;
    this.option_files.forEach(function(v){
        d.options.push(v.send_settings());
    });
    this.bmrs.forEach(function(v){
        d.bmrs.push(v.send_settings());
    });
    return d;
};

//  BMD MODEL OPTIONS
// ===================
var OptionFile = function (session, vals) {
    this.parent = session;
    this.model_name = vals.model_name;
    this.defaults = vals.option_defaults;
    this.override = vals.option_override;
    this.option_override_text = vals.option_override_text;
};

OptionFile.opt_restrict_polynomial = {'0':'None', '-1':'Non-positive', '1':'Non-negative'};
OptionFile.parameter_types = {'d':'Default', 's':'Specified', 'i':'Initialized'};

OptionFile.prototype.default_overrides = function(){
    // Some option files have default overrides specific to the specific
    // endpoint instance; we'll override these defaults here.

    //set the default number of betas equal to number of dose groups - 1
    var beta_models = ['Polynomial', 'Multistage', 'Multistage-Cancer'];
    if ($.inArray(this.model_name, beta_models) >= 0){
        var degree_poly = Math.min(this.parent.endpoint.data.dr.length-1, 8);
        this.override['degree_poly'] = degree_poly;
        this.option_override_text.push('Degree of Polynomial = ' + degree_poly);
    }

    // restrict polynomials betas to be all-positive or all-negative
    if (this.model_name == "Polynomial"){
        var restrict_polynomial;
        if (this.parent.endpoint.data.dataset_increasing){
            restrict_polynomial = '1';
        } else {
            restrict_polynomial = '-1';
        }
        this.override['restrict_polynomial'] = restrict_polynomial;
        this.option_override_text.push('Restrict Polynomial = ' +
            OptionFile.opt_restrict_polynomial[restrict_polynomial]);
    }
};

OptionFile.prototype.add_details = function(){
    var td = $('#bmd_settings_form').data('td_details');
    td.empty();
    $.each(this.option_override_text, function(i, v) {
        td.append(v);
        td.append('<br>');
    });
};

OptionFile.prototype.save = function(){
    var vals = {},
        option_override_text = [],
        success = true;

    $('#bmd_settings_form div.control-group').each(function(index) {
        var field = $(this).data('v'),
            id = field[0],
            name = field[1]['n'], v;

        switch (field[1]['t']){
            case 'i': // integer
                v = parseInt($('#bmd_setting_' + id).val());
                if (!isInt(v)) {
                    alert('Integer field required: "' + $('#bmd_setting_' + id).val() + '" in ' + name);
                    success = false;
                }

                if ( v != field[1]['d']){
                    vals[id] = v;
                    option_override_text.push(name + ' = ' + v);
                }
                break;
            case 'd': // decimal
                v = parseFloat($('#bmd_setting_' + id).val());
                if (!isFloat(v)) {
                    alert('Float field required: "' + $('#bmd_setting_' + id).val() + '" in ' + name);
                    success = false;
                }

                if ( v != field[1]['d']){
                    vals[id] = v;
                    option_override_text.push(name + ' = ' + v);
                }
                break;
            case 'b': // boolean
                v = $('#bmd_setting_' + id).prop('checked');
                if (v+0 != field[1]['d']){
                    vals[id] = v+0;
                    option_override_text.push(name + ' = ' + v);
                }
                break;
            case 'rp': // restrict polynomial
                v = ($('#bmd_setting_' + id + ' option:selected').val()).toString();
                vals[id] = v;
                if (v !== 0 ){
                    option_override_text.push(name + ' = ' + OptionFile.opt_restrict_polynomial[v]);
                }
                break;
            case 'dd': // drop-dose
                v = parseInt($('#bmd_setting_' + id + ' option:selected').val());
                if ( v != field[1]['d']){
                    vals[id] = v;
                    option_override_text.push(name + ' = ' + v);
                }
                break;
            case 'p': //parameters
                var ptype = $('#bmd_setting_' + id + '_type option:selected').val(),
                    ptext = $('#bmd_setting_' + id + '_type option:selected').text(),
                    pval = $('#bmd_setting_' + id + '_value').val();
                if ((pval != '') && !isFloat(parseFloat(pval))) {
                    alert('Float field required: "' + pval + '" in ' + name);
                    success = false;
                }

                v = ptype + '|' + pval;

                if ( v != field[1]['d']){
                    vals[id] = v;
                    option_override_text.push(name + ' = ' + ptext + ' to ' + pval);
                }
                break;
            default:
                console.log('Error in OptionFile.prototype.save');
        }
    });

    if (success === true) {
        this.override = vals;
        this.option_override_text = option_override_text;
        this.add_details();
    }
    return success;
};

OptionFile.prototype.reset = function(){
    this.override = {};
    this.option_override_text = [];
    this.default_overrides();
    this.build_settings_form();
    this.add_details();
};

OptionFile.variance_models = {0:'Modeled Variance', 1:'Constant Variance'};

OptionFile.prototype.build_option_field = function(id, item){
    //build field based on field type
    var div = $('<div class="control-group form-row"></div>'),
        n = item['n'],
        dataset = $('#bmd_dr_tbl').data('d').data;

    div.data('v', [id,item]);
    div.append('<label class="control-label">' + n + '</label>');
    var inp_div = $('<div class="controls"></div>');

    if (id in this.override) {
            v = this.override[id];
        } else {
            v = item['d'];
        }

    switch (item['t']){
        case 'i': // integer
            inp_div.append('<input id="bmd_setting_' + id + '" value="' + v + '">');
            break;
        case 'd': // decimal
            inp_div.append('<input id="bmd_setting_' + id + '" value="' + v + '"">');
            break;
        case 'b': // boolean
            inp_div.append($('<input id="bmd_setting_' + id + '" type="checkbox">').prop('checked', (v > 0)));
            break;
        case 'dd': // drop-dose
            sel = $('<select id="bmd_setting_' + id + '"></select>');
            var l = dataset.dr.length-2; // must have 2 dose-groups
            for (var i = 0; i <= l; i++) {
                (v == i) ? (val='selected') : (val='');
                sel.append('<option value="' + i + '" ' + val + '>' + i + '</option>');
            }
            inp_div.append(sel);
            break;
        case 'rp': // restrict polynomial
            inpsel = $('<select id="bmd_setting_' + id + '"></select>');
            if (v[0] !== undefined){
                var opt_val = (v[0]).toString();
            } else {
                var opt_val = undefined;
            }
            for (var k in OptionFile.opt_restrict_polynomial){
                (opt_val == parseInt(k)) ? (sel = ' selected') : (sel = '');
                inpsel.append('<option value=' + k + ' ' + sel + '>' + OptionFile.opt_restrict_polynomial[k] + '</option>');
            }
            inp_div.append(inpsel);
            break;
        case 'p': // bmd parameter
            v = v.split('|');
            var inpsel = $('<select class="inp_selector" id="bmd_setting_' + id + '_type"></select>');
            $.each(OptionFile.parameter_types, function(key, val) {
                (v[0] == key) ? (sel = ' selected') : (sel = '');
                inpsel.append('<option value="'+ key + '"'+ sel +'>' + val + '</option>');
            });
            inp_div.append(inpsel);
            if( v[0] == 'd'){
                var state = 'disabled';
            } else {
                var state = '';
            }
            inp_div.append('<input ' + state + ' id="bmd_setting_' + id + '_value" value="' + v[1] + '"">');
            break;
        default:
            inp_div.append('<input value="Error in specification">');
    }
    div.append(inp_div);
    return div;
};

OptionFile.prototype.build_option_row = function(id,item){
    //build field based on field type
    var tr = $('<tr></tr>');
    tr.append('<th>' + item['n'] + '</th>');

    if (id in this.override) {
            v = this.override[id];
        } else {
            v = item['d'];
        }

    switch (item['t']){
        case 'i': // integer
        case 'd': // decimal
        case 'dd': // drop-dose
            tr.append('<td>' + v + '</td>');
            break;
        case 'rp': // restrict polynomial
            v = v.toString();
            tr.append('<td>' + OptionFile.opt_restrict_polynomial[v] + '</td>');
            break;
        case 'b': // boolean
            var bool = (v == 1);
            tr.append('<td>' + bool + '</td>');
            break;
        case 'p': // bmd parameter
            v = v.split('|');
            if (v[0] == 'd'){
                tr.append('<td>' + OptionFile.parameter_types[v[0]] + '</td>');
            } else {
                tr.append('<td>' + OptionFile.parameter_types[v[0]] +': ' + v[1] + '</td>');
            }
            break;
        default:
            inp_div.append('<input value="Error in specification">');
    }
    return tr;
};

OptionFile.prototype.build_settings_form = function(td_details){
    //change title
    $('#bmd_settings_form').data('opt',this).data('td_details',td_details);
    $('#bmd_settings_form h3')
        .text('HAWC BMDS {0}: {1} Model Options'
            .printf(this.parent.bmds_version, this.model_name));
    cw = {'op':'#bmd_settings_optimizer',
          'ot':'#bmd_settings_other',
          'p':'#bmd_settings_parameters'};

    // clear old forms
    for (var fieldset in cw) {
        $(cw[fieldset]).empty();
    }

    optionfile = this;
    //add options to field
    $.each(optionfile.defaults, function(k, v) {
        $(cw[v['c']]).append(optionfile.build_option_field(k, v));
    });
};

OptionFile.prototype.build_settings_tbl = function(td_details){
    //change title
    $('#bmd_settings_form').data('opt',this).data('td_details',td_details);
    $('#bmd_settings_form h3')
        .text('HAWC BMDS {0}: {1} Model Options'
            .printf(this.parent.bmds_version, this.model_name));
    cw = {'op':'#bmd_settings_optimizer',
          'ot':'#bmd_settings_other',
          'p':'#bmd_settings_parameters'};

    // clear old forms
    for (var fieldset in cw) {
        $(cw[fieldset]).empty();
    }

    optionfile = this;
    //add options to field
    $.each(optionfile.defaults, function(k, v) {
        $(cw[v['c']]).append(optionfile.build_option_row(k, v));
    });
};

OptionFile.prototype.option_summary_row = function(){
    //returns a row to be inserted into the bmd_setup_tbl table
    var txt = '';
    $.each(this.option_override_text, function(i, v) {
        txt = txt + v + '<br>';
    });
    if (crud == 'Read'){
        crud_txt = 'view';
    } else{
        crud_txt = 'edit'; }
    var row = $('<tr></tr>').data('bmd_option', this);
    row.append('<td>' + this.model_name + '</td>')
       .append('<td>' + txt + '</td>')
       .append('<td><a class="bmd_edit" href="#">' + crud_txt + '</a></td>');
    this.summary_row = row;
    return this.summary_row;
};

OptionFile.prototype.option_delete = function(){
    for(var i=0; i<this.parent.option_files.length; i++){
        if(this.parent.option_files[i] === this){
            this.summary_row.remove();
            this.parent.option_files.splice(i,1);
        }
    }
};

OptionFile.prototype.send_settings = function(){
    // send settings in json form back to server
    // requires- send override text and modified
    var v = {'model_name': this.model_name,
             'override': this.override,
             'override_text': this.option_override_text};
    return v;
};

OptionFile.prototype.get_variance_model = function(){
    // 1 == constant-variance, 0 == modeled-variance
    if (this.defaults.hasOwnProperty('constant_variance')){
        if (this.override.hasOwnProperty('constant_variance')){
            return this.override.constant_variance;
        } else {
            return this.defaults.constant_variance.d;
        }
    } else {
        return undefined;
    }
};

OptionFile.toggle_variance = function(model_list){
    // toggle variance all variance models
    model_list.forEach(function(v){
        if (v.defaults.hasOwnProperty('constant_variance')){
            var val;
            if (v.override.hasOwnProperty('constant_variance')){
                val = (v.override.constant_variance==1) ? 0 : 1;
                var txts = v.option_override_text;
                v.override.constant_variance = val;
                txts.forEach(function(txt, i){
                    if(txt.search('Constant Variance = ')>=0){
                        txts[i] = 'Constant Variance = ' + (val==1);
                    }
                });
            } else {
                val = (v.defaults.constant_variance.d==1) ? 0 : 1;
                v.override['constant_variance'] = val;
                v.option_override_text.push(v.defaults.constant_variance.n + ' = ' + (val==1));
            }
        }
    });
    if (model_list.length > 0){model_list[0].parent.print_options();}
};

//  BMR OPTIONS
// =============

var BMR = function(session, v){
    this.parent = session;
    this.type = v.type;
    this.value = v.value;
    this.confidence_level = v.confidence_level;
};

// used for naming on BMR tables
BMR.table_type_dict = {
    'Extra': '%',
    'Added': '% AR',
    'Abs. Dev.': 'AD',
    'Std. Dev.': 'SD',
    'Rel. Dev.': '% RD',
    'Point': 'Pt'
};

BMR.prototype.clone = function(){return new BMR(this.parent, this);};

BMR.prototype.send_settings = function(){
    // send settings in json form back to server
    var v = {'confidence_level': this.confidence_level,
             'type'  : this.type,
             'value' : this.value };
    return v;
};

BMR.prototype.value_pretty = function(){
    switch (this.type){
        case 'Extra':
        case 'Added':
        case 'Rel. Dev.':
            return this.value*100.0 + "%";
        case 'Abs. Dev.':
        case 'Std. Dev.':
        case 'Point':
            return this.value;
        default:
            return this.value;
    }
};

BMR.prototype.build_settings_form = function(row){

    //bind object form
    $('#bmr_settings_form').data('bmr', this);
    $('#bmr_settings_form').data('row', row);

    var bmr_type = this.type;
    //add options to BMR type
    $('#bmr_type').empty();
    $.each($('#bmr_select option'), function(i, v) {
        if ($(v).text()==bmr_type) {
            s = 'selected';
        } else {
            s = '';
        }
        $('#bmr_type').append('<option ' + s + '>' + $(v).text() +'</option>');

    });
    $('#bmr_value')[0].value = this.value;
    $('#bmr_confidence_level')[0].value = this.confidence_level;
};

BMR.prototype.build_settings_tbl = function(row){
    $('#bmr_type').html(this.type);
    $('#bmr_value').html(this.value_pretty());
    $('#bmr_confidence_level').html(this.confidence_level);
};

BMR.prototype.is_between_range = function(val, low, high){
    //checks that value is between a range, exclusive
    return !(!isFloat(val) || val < low || val > high);
};

BMR.prototype.is_bmr_valid = function(type, value){
    var valid = true;
    switch (type){
        case 'Extra':
        case 'Added':
            valid = this.is_between_range(value, 0, 1);
            if (!valid) {
                alert('BMR value must be between 0 and 1 for this BMR type.');
            }
            break;
        case 'Abs. Dev.':
        case 'Std. Dev.':
        case 'Rel. Dev.':
        case 'Point':
        case 'Extra':
            valid = true;
            break;
        default:
            valid = false;
            console.log('default BMR prototype called.');
    }
    return valid;
};

BMR.prototype.option_summary_row = function(){
    //returns a row to be inserted into the BMR summary table
    txt = (crud == 'Read') ? 'view' : 'edit';
    var row = $('<tr></tr>').data('bmr', this);
    row.append('<td>' + this.type + '</td>')
       .append('<td>' + this.value_pretty() + '</td>')
       .append('<td>' + this.confidence_level + '</td>')
       .append('<td><a class="bmr_edit" href="#">' + txt + '</a></td>');
    this.summary_row = row;
    return this.summary_row;
};

BMR.prototype.save_from_form = function(){
    // return true if success, else false

    var confidence_level = parseFloat($('#bmr_confidence_level').val()),
        type = $('#bmr_type > option:selected').val(),
        value = parseFloat($('#bmr_value').val());

    //QA checks fields are appropriate
    var error = false;

    // make sure confidence_level is b/w 0 and 1
    if (!this.is_between_range(confidence_level,0,1)) {
        alert('BMR confidence level must be between 0 and 1.');
        error = true;
    }
    // make sure BMR is within valid range
    if (!this.is_bmr_valid(type, value)) {error = true;}
    if (error) { return false; }

    //If true, update model
    this.type = type;
    this.value = value;
    this.confidence_level = confidence_level;

    //update table row view and close form
    var row = $('#bmr_settings_form').data('row');
    if (row == 'new') {this.parent.add_bmr(this);}
    this.parent.print_bmrs();
    return true;
};

BMR.prototype.remove = function(){
    for(var i=0; i<this.parent.bmrs.length; i++){
        if(this.parent.bmrs[i] === this){
            this.summary_row.remove();
            this.parent.bmrs.splice(i,1);
        }
    }
};

BMR.prototype.get_table_name = function(){
    // Return the proper table-formatted name for the selected BMR-type.
    switch (this.type){
        case 'Extra':
        case 'Added':
        case 'Rel. Dev.':
            return this.value*100 + BMR.table_type_dict[this.type];
        case 'Abs. Dev.':
        case 'Std. Dev.':
        case 'Point':
            return this.value + BMR.table_type_dict[this.type];
        default:
            return this.value + ' ' + this.type;
    }
};

//  BMD OUTPUT
// ============
var BMDOutput = function(session, outputs, options, bmr) {
    this.parent = session;
    this.options = options;
    this.id = outputs.id;
    this.model_name = outputs.model_name;
    this.outputs = outputs.outputs;
    this.output_text = outputs.output_text;
    this.plotting = outputs.plotting;
    this.bmds_plot_url = outputs.bmds_plot_url;
    this.option_id = outputs.option_id;
    this.bmr_id = outputs.bmr_id;
    this.bmr = bmr;
    this.bin_logic = 0;
    this.bin_override = outputs.override; // 0 = valid, 1 = questionable, 2 = unusable, 99= N/A
    this.bin_override_notes = outputs.override_text;
    this.get_recommendations();
};

BMDOutput.prototype.submit = function(){
    return {'id': this.id,
            'override': this.bin_override,
            'override_text': this.bin_override_notes};
};

BMDOutput.prototype.get_bin = function(){
    return ((this.bin_override !== undefined) && (this.bin_override!==99)) ? this.bin_override : this.bin_logic;
};

BMDOutput.prototype.show_modal = function(dr_plot){
    $('#bmd_raw_output_label').html(this.model_name + ' Output');
    $('#raw_output_text').html(this.output_text);
    $('#bmd_raw_output_label').data('d',this);
    raw_output_img.clear_bmd_lines('d3_bmd_selected');
    raw_output_img.clear_bmd_lines();
    raw_output_img.add_bmd_line($('#bmd_raw_output_label').data('d'));
    $('#bmd_raw_output').modal({
            backdrop: true,
            keyboard: true
        });
};

BMDOutput.prototype.get_recommendations = function(){
    // Generate customized model recommendations for output model based on the
    // logic-list and the outputs for the selected model. Also update overall
    // bin placement for the model.
    var t = this;
    recommendations = [];
    this.parent.logic_list.items.forEach(function(v,i){
        recommendations.push(new BMD_UnitTests(t, v));
    });
    this.recommendations = recommendations;

    //Place each model in object bin, and build summary-text for bin.
    var bin = 0,
        bin_text = [[], [], [], []]; // index 3 is success
    this.recommendations.forEach(function(v){
        bin = Math.max(bin, v.bin);
        if ((!v.pass) && (v.text!=='')){
            bin_text[v.bin].push(v.text);
        } else if (v.text!==''){
            bin_text[3].push(v.text);
        }
    });
    this.bin_logic = bin;
    this.bin_text = bin_text;
};

//  BMD OUTPUT TABLE
// =================
var OutputTable = function(tbl_selector, session){
    this.tbl = $(tbl_selector);
    this.parent = session;
    this.bmr_of_interest = 0; //todo - move to session?
    this.set_columns();
    this.build_table();
};

OutputTable.prototype.clear = function(){
    this.tbl.find('thead').html('');
    this.tbl.find('tbody').html('');
};

OutputTable.prototype.build_table = function(){
    this.clear();
    this.build_header();
    this.build_data_rows();
};

OutputTable.prototype.set_columns = function(){
    // should be able to customize in the future

    // set columns
    var ot = this;
    this.columns = [];
    this.columns.push(this.add_column('model_name', 'Model'));
    this.columns.push(this.add_column('p_value4', 'Global <br><i>p</i>-value'));
    this.columns.push(this.add_column('AIC', 'AIC'));

    // BMD/BMDL for each bmr
    this.parent.bmrs.forEach(function(v,i){
        var bmr_str = v.get_table_name();
        ot.columns.push(ot.add_column('BMD', 'BMD<br>(' + bmr_str + ')', i));
        ot.columns.push(ot.add_column('BMDL', 'BMDL<br>(' + bmr_str + ')', i));
    });

    this.columns.push(this.add_column('residual_of_interest', 'Residual <br>of Interest'));
    this.columns.push(this.add_column('OutputFile', 'Output<br>File')); // special case
};

OutputTable.prototype.add_column = function(field_name, column_name, bmr_id){
    if (bmr_id === undefined) {bmr_id = this.bmr_of_interest;}
    return {'field_name': field_name, 'column_name': column_name, 'bmr_id': bmr_id};
};

OutputTable.prototype.set_bmr_of_interest = function(index){
    if (index < this.parent.bmrs.length){
        this.bmr_of_interest = index;
    }
};

OutputTable.prototype.build_header = function(){
    // Build table header based on the BMR types available for modeling
    var tr = $('<tr></tr>');
    this.columns.forEach(function(v){
        tr.append('<th>' + v.column_name + '</th>');
    });
    this.tbl.find('thead').html(tr);
};

OutputTable.prototype.build_data_rows = function(){
    this.tbl.find('tbody').empty();
    var ot = this;
    this.parent.outputs.forEach(function(v){
        ot.build_row(v);
    });
};

OutputTable.prototype.build_row = function(option_row){
    // Build data row for output table. The entire row apends the output file
    // of interest for the BMR of interest; the individual BMD/BMDL rows also
    // append the output file for the other BMRs in the table. These are used
    // to build output figures.
    var tr = $('<tr></tr>').data('d', option_row[this.bmr_of_interest]), td;
    this.columns.forEach(function(v){
        switch(v.field_name){
            case 'OutputFile':
                tr.append('<td><a class="bmd_outfile" href="#">View</a></td>');
                break;
            case 'BMD':
            case 'BMDL':
                td = $('<td>' + option_row[v.bmr_id].outputs[v.field_name] +  '</td>').data('d', option_row[v.bmr_id]);
                tr.append(td);
                break;
            default:
                tr.append('<td>' + option_row[v.bmr_id].outputs[v.field_name] + '</td>');
        }
    });
    this.tbl.find('tbody').append(tr);
};

//  SELECTION
// ==========
var Selection = function(session){
    // Selector exists when a session has been run
    this.parent = session;
    this.bmr_id = null;
    this.model_id = null;
    this.notes = '';
    this.selected_row = null;
    this.BMDOutput = null;
    this.load_session_values();
    this.build_html();
};

Selection.prototype.load_session_values = function(){
    // preload the session values, if any are available
    this.notes = this.parent.session.notes;
    if (this.parent.session.selected_model == -1){
        this.bmr_id = -1;
        this.model_id = -1;
    } else {
        var bmr_id, model_id, id = this.parent.session.selected_model;
        this.parent.outputs.forEach(function(model_type){
            model_type.forEach(function(model){
                if (model.id == id){
                    bmr_id = model.bmr_id;
                    model_id = model.option_id;
                }
            });
        });
        this.bmr_id = bmr_id;
        this.model_id = model_id;
    }
};

Selection.prototype.build_html = function(){
    this.clear();
    if(this.parent.outputs.length>0){
        if(this.parent.crud == 'Read'){
            this.build_table();
        } else {
            this.build_form();
        }
    }
};

Selection.prototype.clear=  function(){
    $('#selection_div').html('');
};

Selection.prototype.build_form = function(){
    // build model selection form
    var div = $('<div id="selection_div" class="row-fluid"></div>'),
        form = $('<form id="selection_form" class="form-horizontal"></form>'),
        formset = $('<formset></formset>');

    formset.append('<legend>Model selection</legend>');
    formset.append('<span class="help-block">Select best-fitting BMD model</span>');

    inputs=[];

    var add_input_row = function(label_text, input_field){
        var input_row = $('<div class="control-group form-row"></div>');
        input_row.append('<label class="control-label">{0}</label>'.printf(label_text));
        var control_div = $('<div class="controls"></div>');
        control_div.append(input_field);
        input_row.append(control_div);
        return input_row;
    };

    // add bmr button
    var inp_bmr = $('<select id="selection_bmr" class="span8"></select>');
    this.parent.bmrs.forEach(function(v,i){
        inp_bmr.append('<option value=' + i + '>' + v.get_table_name() + '</option>');
    });
    inputs.push(add_input_row("Selected BMR:", inp_bmr));

    // add bmd option
    var inp_bmd = $('<select id="selection_model" class="span8"></select>');
    inp_bmd.append('<option value="-1">None</option>');
    this.parent.outputs.forEach(function(v){
        inp_bmd.append('<option value=' + v[0].option_id + '>' + v[0].model_name + '</option>');
    });
    inputs.push(add_input_row("Selected Model:", inp_bmd));

    // add notes
    var inp_txt = $('<textarea id="selection_notes" class="span8">{0}</textarea>'.printf(this.notes));
    inputs.push(add_input_row("Selection Notes:", inp_txt));

    // add csrf token
    inputs.push(csrf_token);

    //add buttons
    var buttons = $('<div class="form-actions"></div>');
    buttons.append('<a id="selection_submit" href="#" class="btn btn-primary">Select</a>');

    formset.append(inputs, buttons);
    form.append(formset);
    div.append(form);
    $('#bmd_output_tbl').after(div);

    // add event-binding
    var obj = this;
    $('#selection_form').on('change', '#selection_model', function(e){
        obj.test_row_highlight();
    });
    $('#selection_form').on('change', '#selection_bmr', function(e){
        obj.bmr_change();
        obj.test_row_highlight();
    });
    $('#selection_form').on('click', '#selection_submit', function(e){
        e.preventDefault();
        obj.submit();
    });

    // select proper model
    $('#selection_bmr option[value="' + this.bmr_id + '"]').prop('selected', true);
    $('#selection_model option[value="' + this.model_id + '"]').prop('selected', true);
    this.test_row_highlight();
};

Selection.prototype.bmr_change = function(){
    // update the models displayed on the plot to use the proper BMR.
    var bmr_id = parseInt($($('#selection_bmr option:selected')[0]).val());
    this.parent.output_tbl.set_bmr_of_interest(bmr_id);
    this.parent.output_tbl.build_data_rows();
};

Selection.prototype.build_table = function(){
    // build table view
    this.find_selected_row();
    this.highlight_row();
    var bmr, model_name;
    var div = $('<div id="selection_div" class="row-fluid"></div>'),
        tbl = $('<table id="selection_table" class="table table-striped table-condensed"><colgroup><col style="width: 30%;"><col style="width: 70%;"></colgroup><tbody></tbody></table>');
    try {
        bmr = this.parent.bmrs[this.bmr_id].get_table_name();
    } catch(err) {
        bmr = 'None selected.';
    }
    try {
        model_name = this.BMDOutput.model_name;
    } catch(err) {
        model_name = 'None selected.';
    }
    tbl.append('<tr><th>BMR</th><td>' + bmr + '</td></tr>');
    tbl.append('<tr><th>Model</th><td>' + model_name +'</td></tr>');
    tbl.append('<tr><th>Notes</th><td>' + this.notes +'</td></tr>');
    div.append(tbl);
    $('#bmd_output_tbl').after(div);
};

Selection.prototype.test_row_highlight = function(){
    // check if a row can be highlighted, if it can, highlight
    this.bmr_id = parseInt($($('#selection_bmr option:selected')[0]).val());
    this.model_id = parseInt($($('#selection_model option:selected')[0]).val());
    this.notes = $('#selection_notes').val();
    this.reset_selection();
    if ((this.bmr_id >= 0) && (this.model_id >= 0)) {
        this.find_selected_row();
        this.highlight_row();
    }
};

Selection.prototype.highlight_row = function(){
    // highlight selected row
    if (this.selected_row !== null) {
        this.selected_row.addClass('bmd_selected_model');
        bmd_output_plot.clear_bmd_lines('d3_bmd_selected');
        bmd_output_plot.add_bmd_line(this.BMDOutput, 'd3_bmd_selected');
    }
};

Selection.prototype.rebuild_plot = function(){
    bmd_output_plot.build_plot();
};

Selection.prototype.find_selected_row = function(){
    // find the selected row and returns
    var trs = this.parent.output_tbl.tbl.find('tbody tr'),
        model_id = this.model_id,
        tr = null;
    $.each(trs, function(i,v){
        var d = $(v).data('d');
        if(d.option_id == model_id){
            tr = $(v);
        }
    });
    if(tr !== null){
        this.selected_row = tr;
        this.BMDOutput = tr.data('d');
    }
};

Selection.prototype.reset_selection = function(){
    // unighlight selected row and reset properties
    bmd_output_plot.clear_bmd_lines('d3_bmd_selected');
    if (this.selected_row !== null){
        this.selected_row.removeClass('bmd_selected_model');
        this.selected_row = null;
        this.BMDOutput = null;
    }
};

Selection.prototype.submit = function(){
    // Submit data to server via AJAX response, then redirect to summary view
    this.test_row_highlight();
    var model = (this.selected_row === null) ? null : this.BMDOutput.id;
    overrides = [];
    this.parent.outputs.forEach(function(v){
        v.forEach(function(d){
            overrides.push(d.submit());
        });
    });
    var args = {
            'model': model,
            'notes': this.notes,
            'overrides': overrides};
    args = JSON.stringify(args);
    var url = '/bmd/model/' + this.parent.session.pk + '/select/';
    var redirect_url = '/ani/endpoint/' + this.parent.endpoint.data.pk  + '/';
    $.post(url, args, function(d) {
        document.location.href= redirect_url;
    });
};

//  LOGIC ITEM
// ===========
var LogicItem = function(item){
    // individual logic-item, uncoupled to output file and specific to session.
    this.short_name = item.name;
    this.name = item.description;
    this.threshold = item.threshold;
    this.bin = item.failure_bin;
    this.func = item.function_name;
    this.logic_id = item.logic_id;
    this.test_on = item.test_on;
    this.last_updated = item.last_updated;
};

//  LOGIC LIST
// ===========
var LogicList = function(session, items){
    // unpack logic-list and save as object
    this.parent = session;
    var l = [],
        last_updated = items[0].last_updated;
    items.forEach(function(v){
        if (v.test_on){
            l.push(new LogicItem(v)) ;
            if (v.last_updated > last_updated){last_updated = v.last_updated;}
        }
    });
    this.last_updated = last_updated;
    this.items = l;
    this.add_update_warning();
};

LogicList.prototype.add_update_warning = function(){
    if ((crud!='Create') && (this.parent.session.last_updated < this.last_updated)){
        $('#warnings').prepend('<div class="alert alert-danger "><button ' +
          'type="button" class="close" data-dismiss="alert">×</button>'+
          '<h4>Warning!</h4>BMD model recommendation logic has changed since '+
          'the BMD session was last updated. Please review BMD model selections'+
          ' and re-save to remove this message.</div>');
    }
};

//  TBL_RECOMMENDATION
// ===================
var Tbl_Recommendation = function(session){
    this.parent = session;
    this.build_table();
  };

Tbl_Recommendation.bin_names = {0: 'Viable', 1: 'Questionable', 2: 'Not Viable', 99: 'N/A'};

Tbl_Recommendation.prototype.add_footnote_rows = function(){
    var tfoot = $('<tfoot></tfoot>');
    tfoot.append('<tr><td colspan="100">Recommended model(s) highlighted in green.</td></tr>');
    tfoot.append('<tr><td colspan="100">Selected model highlighted in yellow.</td></tr>');
    this.tbl.append(tfoot);
};

Tbl_Recommendation.prototype.add_header_rows = function(){
    var thead = $('<thead></thead>');
    var tr =  $('<tr></tr>');
    var cols = ['Model Name', 'AIC', 'BMD', 'BMDL','Notes','Warnings', 'Overall bin', 'Override'];
    cols.forEach(function(v,i){
        tr.append('<th>' + v + '</th>');
    });
    thead.append(tr);
    this.tbl.append(thead);
};

Tbl_Recommendation.prototype.add_data_rows = function(){
    var t = this,
        bmr = this.parent.output_tbl.bmr_of_interest;
    this.parent.outputs.forEach(function(v, i){
        var tr = $('<tr></tr>').data('d', v),
            vals = v[bmr];
        if (t.parent.selection.BMDOutput === v[bmr]){
            tr.addClass('bmd_selected_model');
        }
        tr.append('<td>' + vals.model_name + '</td>');
        tr.append('<td>' + vals.outputs.AIC + '</td>');
        tr.append('<td>' + vals.outputs.BMD + '</td>');
        tr.append('<td>' + vals.outputs.BMDL + '</td>');
        //print success
        var popup_text = vals.bin_text[3].join('<br>');
        tr.append('<td><a href="#" class="logic_popovers" data-placement="bottom"' +
                      ' data-trigger="hover" data-toggle="popover" data-content="' +
                      popup_text + '" data-original-title="Success Messages">' +
                      vals.bin_text[3].length + '</a></td>');

        //print failure
        var l = 0,
            cls = 'logic_test_pass';
        popup_text = '';

        if (vals.bin_text[0].length > 0){
            cls = 'logic_test_warning';
            l += vals.bin_text[0].length;
            popup_text += '<b>Warnings</b><br>' + vals.bin_text[0].join('<br>') + '<br>';
        }
        if (vals.bin_text[1].length > 0){
            cls = 'logic_test_questionable';
            l += vals.bin_text[1].length;
            popup_text += '<b>Questionable Warnings</b><br>' + vals.bin_text[1].join('<br>') + '<br>';
        }
        if (vals.bin_text[2].length > 0){
            cls = 'logic_test_fail';
            l += vals.bin_text[2].length;
            popup_text += '<b>Serious Warnings</b><br>' + vals.bin_text[2].join('<br>');
        }
        var td = $('<td></td>').addClass(cls);
        td.append('<a href="#" class="logic_popovers" data-placement="bottom"' +
                  ' data-trigger="hover" data-toggle="popover" data-content="' +
                  popup_text + '" data-original-title="Warnings">' +
                  l + '</a>');
        tr.append(td);
        tr.append(t.get_recommendation_field(vals));
        tr.append('<td class=recommend_override>' +  Tbl_Recommendation.bin_names[vals.bin_override]+ '</td>');
        t.tbl.append(tr);
    });
};

Tbl_Recommendation.prototype.get_recommendation_field = function(model){
    // Return the model recommendation cell, with custom settings.
    var td = $('<td></td>');
    if (model.recommended){
        td.append('Recommended model' + model.recommended_reason);
        td.addClass('bmd_recommended_model');
    } else if (model.get_bin() === 0) {
        td.append('Alternate');
    } else{
        td.append(Tbl_Recommendation.bin_names[model.get_bin()]);
    }
    return td;
};

Tbl_Recommendation.prototype.clear = function(){$('#recommendation_tbl_div').empty();};

Tbl_Recommendation.prototype.build_table = function(){
    // create table and h1 header to create decision-logic table
    this.clear();
    var div = $('#recommendation_tbl_div');
    div.append('<h3>Recommendations to assist BMD Model Selection</h3>');

    this.tbl = $('<table id="recommendation_tbl" class="table table-condensed"></table>');
    this.get_recommended_model();
    this.add_header_rows();
    this.add_footnote_rows();
    this.add_data_rows();
    div.append(this.tbl);

    // turn on popovers
    $(".logic_popovers").popover({ html : true });

    //turn on override-detection
    $(this.tbl).on('click', '.recommend_override', function(e){
        d = $(this).parent().data('d');
        session.recommendation_table.clear_override();
        if (session.crud == 'Read'){
            session.recommendation_table.build_override_table(d);
        } else {
            session.recommendation_table.build_override_form(d);
        }
    });
};

Tbl_Recommendation.prototype.build_override_form = function(outputs){
    var output = outputs[outputs[0].parent.output_tbl.bmr_of_interest];
    $('#override_div').css('display','block').data('d', output);
    $('#override_model_description').html(output.model_name + ' (' + output.bmr.get_table_name() + ')');
    $('#override_status').val(output.bin_override);
    $('#override_notes').val(output.bin_override_notes);

    $('#override_status').change(function(){
        val = parseInt($(this).val());
        $('#override_div').data('d').bin_override = val;
        session.recommendation_table.build_table();
    });
    $('#override_notes').keyup(function(){
        $('#override_div').data('d').bin_override_notes = $(this).val();
    });
};

Tbl_Recommendation.prototype.build_override_table = function(outputs){
    var output = outputs[outputs[0].parent.output_tbl.bmr_of_interest];
    $('#override_model_description').html(output.model_name + ' (' + output.bmr.get_table_name() + ')');
    $('#override_status').html(Tbl_Recommendation.bin_names[output.bin_override]);
    $('#override_notes').html(output.bin_override_notes);
    $('#override_div').css('display','block');
};

Tbl_Recommendation.prototype.clear_override = function(){
    $('#override_div').css('display','none');
};


Tbl_Recommendation.prototype.get_recommended_model = function(){
    // returns the recommended model in the logic bin, or undefined. Only
    // searches cases where bin=0
    var max_diff = this.maximum_BMDL_difference();
    if (max_diff === undefined){return undefined;}

    var models, reason, field;
    if (max_diff > this.parent.session.sufficiently_close_BMDL){
        field = 'BMDL';
        reason = '<br>(lowest BMDL)';
    } else {
        field = 'AIC';
        reason = '<br>(lowest AIC)';
    }
    var minimum = this.get_minimum(field);
    var bmr = this.parent.output_tbl.bmr_of_interest;
    this.parent.outputs.forEach(function(v){
        if (v[bmr].get_bin() === 0 &&
            ((v[bmr].outputs.hasOwnProperty(field)) &&
            (v[bmr].outputs[field] == minimum))){
            v[bmr].recommended = true;
            v[bmr].recommended_reason = reason;
        } else {
            v[bmr].recommended = false;
            v[bmr].recommended_reason = '';
        }
    });
};

Tbl_Recommendation.prototype.get_minimum = function(field){
    var minimum, test;
    var bmr = this.parent.output_tbl.bmr_of_interest;
    this.parent.outputs.forEach(function(v){
        if (v[bmr].get_bin() === 0 &&
            v[bmr].outputs.hasOwnProperty(field) &&
            v[bmr].outputs[field] != -999){
            test = v[bmr].outputs[field];
            if (minimum === undefined){
                minimum = test;
            } else {
                minimum = Math.min(minimum, test);
            }
        }
    });
    return minimum;
};

Tbl_Recommendation.prototype.maximum_BMDL_difference = function(){
    // finds the maximum BMDL difference of all models in the bin, or undefined
    var min = Infinity,
        max = -Infinity,
        bmr = this.parent.output_tbl.bmr_of_interest;
    this.parent.outputs.forEach(function(v){
        if (v[bmr].get_bin() == 0 &&
            v[bmr].outputs.BMDL > 0){
            min = Math.min(min, v[bmr].outputs.BMDL);
            max = Math.max(max, v[bmr].outputs.BMDL);
        }
    });
    var ratio = max/min;
    return (ratio<Infinity) ? ratio : undefined;
};

//  BMD UNIT TEST
// ==============
var BMD_UnitTests = function(BMDOutput, logic_item){
    this.parent = BMDOutput;
    this.logic_item = logic_item;
    this.pass = true;
    this.text = '';
    this.bin = 0;
    this.test_cases(logic_item.func);
};

BMD_UnitTests.get_numeric_value = function(v){
    if (isFinite(parseFloat(v))){
        return parseFloat(v);
    } else {
        return 0.0001;
    }
};
BMD_UnitTests.get_string_value = function(v){
    if (isFinite(parseFloat(v))){
        return v.toPrecision(4);
    } else {
        return v;
    }
};

BMD_UnitTests.prototype.test_cases = function(key){
    // handler to call proper test-case method
    var methods = {'ggof': this.ggof,
                   'exists_bmd':this.exists_bmd,
                   'exists_bmdl':this.exists_bmdl,
                   'exists_bmdu':this.exists_bmdu,
                   'exists_aic':this.exists_aic,
                   'variance_type':this.variance_type,
                   'variance_fit':this.variance_fit,
                   'bmd_ratio':this.bmd_ratio,
                   'residual':this.residual,
                   'warnings':this.warnings,
                   'high_bmd':this.high_bmd,
                   'high_bmdl':this.high_bmdl,
                   'low_bmd':this.low_bmd,
                   'low_bmdl':this.low_bmdl,
                   'control_residual':this.control_residual,
                   'control_stdev':this.control_stdev};
    return methods[key].apply(this, Array.prototype.slice.call( arguments, 1 ));
};
BMD_UnitTests.prototype.passWhenGreater = function(args){
    try{
        var text = args.text, value, cmp;
        if (args.hasOwnProperty('value')){
            value = args.value;
        } else {
            value = this.parent.outputs[args.field];
        }
        cmp = BMD_UnitTests.get_numeric_value(value);
        if ((cmp != -999) && (isFinite(cmp))){
            if (cmp >= this.logic_item.threshold){
                this.pass=true;
                this.text = text + ' is greater than ' + this.logic_item.threshold + ' (' + BMD_UnitTests.get_string_value(value) +')';
                return true;
            } else {
                this.text ='FAILED: ' + text + ' is less than ' + this.logic_item.threshold +  ' (' + BMD_UnitTests.get_string_value(value) +')';
            }
        } else {
            this.text ='FAILED: ' + text + ' is unspecified';
        }
    } catch(err){
        this.text ='FAILED: error ocured with ' + text + ' test';
    }
    this.pass = false;
    this.bin = this.logic_item.bin;
    return false;
};
BMD_UnitTests.prototype.passWhenLess = function(args){
    try{
        var text = args.text,
            value, cmp,
            abs_val = args.abs_val || false;
        if (args.hasOwnProperty('value')){
            value = args.value;
        } else {
            value = this.parent.outputs[args.field];
        }
        cmp = BMD_UnitTests.get_numeric_value(value);
        if ((cmp != -999) && (isFinite(cmp)) && (!isNaN(value))){
            if (abs_val) {cmp = Math.abs(cmp);}
            if (cmp <= this.logic_item.threshold){
                this.pass=true;
                this.text = text + ' is less than ' + this.logic_item.threshold + ' (' + BMD_UnitTests.get_string_value(value) +')';
                return true;
            } else {
                this.text ='FAILED: ' + text + ' is greater than ' + this.logic_item.threshold +  ' (' + BMD_UnitTests.get_string_value(value) +')';
            }
        } else {
            this.text ='FAILED: ' + text + ' is unspecified';
        }
    } catch(err){
        this.text ='FAILED: error occurred with ' + text + ' test';
    }
    this.pass = false;
    this.bin = this.logic_item.bin;
    return false;
};
BMD_UnitTests.prototype.fieldExists = function(field_name){
    try{
        var f = this.parent.outputs[field_name];
        if ((f != -999) && (f !== undefined)){
            this.pass=true;
            this.text = field_name + ' is a valid value';
            return true;
        } else {
            this.text ='FAILED: ' + field_name + ' is undefined';
        }
    } catch(err){
        this.text ='FAILED: ' + field_name + ' is not found';
    }
    this.pass=false;
    this.bin = this.logic_item.bin;
    return false;
};

// Exists tests
BMD_UnitTests.prototype.exists_bmd = function(){return this.fieldExists('BMD');};
BMD_UnitTests.prototype.exists_bmdl = function(){return this.fieldExists('BMDL');};
BMD_UnitTests.prototype.exists_bmdu = function(){return this.fieldExists('BMDU');};
BMD_UnitTests.prototype.exists_aic = function(){return this.fieldExists('AIC');};

// passWhenLess tests
BMD_UnitTests.prototype.bmd_ratio = function(){
    var ratio, BMD, BMDL;
    try{
        if (this.parent.outputs.BMD != -999){ BMD = this.parent.outputs.BMD; }
        if (this.parent.outputs.BMDL != -999){ BMDL = this.parent.outputs.BMDL; }
        ratio = BMD/BMDL;
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'BMD/BMDL ratio',
                              'value':ratio});
};
BMD_UnitTests.prototype.residual = function(){
    return this.passWhenLess({'text':'Residual of Interest',
                              'field':'residual_of_interest',
                              'abs_val':true});
};
BMD_UnitTests.prototype.high_bmd = function(){
    var ratio, BMD, high_dose;
    try{
        high_dose = this.parent.parent.endpoint.data.dr[this.parent.parent.endpoint.data.dr.length-1].dose; // maximum-dose
        if (this.parent.outputs.BMD != -999){ BMD = this.parent.outputs.BMD; }
        ratio = BMD/high_dose;
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'BMD/high-dose ratio',
                              'value':ratio});
};
BMD_UnitTests.prototype.high_bmdl = function(){
    var ratio, BMDL, high_dose;
    try{
        high_dose = this.parent.parent.endpoint.data.dr[this.parent.parent.endpoint.data.dr.length-1].dose; // maximum-dose
        if (this.parent.outputs.BMDL != -999){ BMDL = this.parent.outputs.BMDL; }
        ratio = BMDL/high_dose;
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'BMDL/high-dose ratio',
                              'value':ratio});
};
BMD_UnitTests.prototype.low_bmd = function(){
    var ratio, BMD, low_dose;
    try{
        low_dose = this.parent.parent.endpoint.data.dr[1].dose; // first non-zero dose
        if (this.parent.outputs.BMD != -999){ BMD = this.parent.outputs.BMD; }
        ratio = low_dose/BMD;
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'BMD/low-dose ratio',
                              'value':ratio});
};
BMD_UnitTests.prototype.low_bmdl = function(){
    var ratio, BMDL, low_dose;
    try{
        low_dose = this.parent.parent.endpoint.data.dr[1].dose; // first non-zero dose
        if (this.parent.outputs.BMDL != -999){ BMDL = this.parent.outputs.BMDL; }
        ratio = low_dose/BMDL;
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'BMDL/low-dose ratio',
                              'value':ratio});
};
BMD_UnitTests.prototype.control_residual = function(){
    // Check residual of control dose (first-dose group)
    var value;
    try {
        value = this.parent.outputs.fit_residuals[0];
    } catch(err) {
        value = undefined;
    }
    return this.passWhenLess({'text':'Control residual',
                              'value':value,
                              'abs_val':true});
};
BMD_UnitTests.prototype.control_stdev = function(){
    // Compare absolute ratio of modeled control standard devation to actual
    // control standard deviation; estimation often used for setting BMR.
    var ratio, stdev_modeled, stdev_actual;
    try{
        stdev_modeled = this.parent.outputs.fit_est_stdev[0];
        stdev_actual = this.parent.outputs.fit_stdev[0];
        ratio = Math.abs(stdev_modeled/stdev_actual);
    } catch(err) {
        ratio = undefined;
    }
    return this.passWhenLess({'text':'Control Stdev Ratio',
                              'value':ratio,
                              'abs_val':true});
};

// passWhenGreater tests
BMD_UnitTests.prototype.ggof = function(){
    return this.passWhenGreater({'text':'Global goodness-of-fit',
                                 'field':'p_value4'});
};

BMD_UnitTests.prototype.variance_fit = function(){
    return this.passWhenGreater({'text':'Global variance model-fit',
                                 'field':'p_value3'});
};

// Custom tests
BMD_UnitTests.prototype.variance_type = function(){
   try{
        var model = this.parent.options.get_variance_model(), // 1 = constant, 0 = modeled
            value = this.parent.outputs['p_value2'],
            cmp;
        if (value != -999){
            if (value == '<0.0001'){cmp = 0.0001;} else {cmp=value;}
            if (((model === 1) && (cmp >= 0.1)) ||
                ((model === 0) && (cmp <= 0.1))){
                this.pass=true;
                this.text = 'Proper variance model selected (' + OptionFile.variance_models[model] + ", p-value 2 = " + value + ')';
                return true;
            } else {
                this.text ='FAILED: incorrect variance model (' + OptionFile.variance_models[model] + ", p-value 2 = " + value + ')';
            }
        } else {
            this.text ='FAILED: corrected variance model is undetermined';
        }
    } catch(err){
        this.text ='FAILED: error ocured with variance-model test';
    }
    this.pass = false;
    this.bin = this.logic_item.bin;
    return false;
};

BMD_UnitTests.prototype.warnings = function(){
    // If any warnings are present, test fails, otherwise successful.
    if (this.parent.outputs.hasOwnProperty('warnings')){
        this.pass = false;
        this.text = this.parent.outputs.warnings.join('\n');
    } else {
        this.pass = true;
        this.bin = this.logic_item.bin;
        this.text = '';
    }
};
