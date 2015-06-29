// Endpoint subclass with editing functionality
var EditEndpoint = function(endpoint, doses, eg_table, plot){
    Endpoint.call(this, endpoint); // call parent constructor
    this.doses = endpoint.doses;
    this.eg_table = eg_table;
    this.plot_div = plot;
    this.inject_doses(doses);
    this.setOELS();
    this.update_endpoint_from_form();
};
_.extend(EditEndpoint, {
    getVarianceType: function(variance_type){
        // static method used for returning the "pretty-name" for variance type
        switch(variance_type){
            case 0:
                return "N/A";
            case 1:
                return "Standard Deviation";
            case 2:
                return "Standard Error";
            case 3:
                return "Not Reported";
            default:
                throw("Unknown variance_type");
        }
    }
});
EditEndpoint.prototype = {
    update_endpoint_from_form: function(){
        var vals = { 'endpoint_group': [] };
        //save form values
        $('#endpoint :input').each(function() {
            vals[this.name] = $(this).val();
        });
        vals['NOEL'] = $('#id_NOEL option:selected').val();
        vals['LOEL'] = $('#id_LOEL option:selected').val();
        vals['FEL'] = $('#id_FEL option:selected').val();

        //now endpoint-group data
        this.eg_table.find('tbody > tr').each(function(i, tr){
            var row = {};
            $(tr).find(':input').each(function(i, d){
                var name = d.name.split("-").pop();
                row[name] = parseFloat(d.value, 10);
            });
            row['isReported'] = $.isNumeric(row['response'] || row['incidence']);
            row['hasVariance'] = $.isNumeric(row['variance']);
            vals['endpoint_group'].push(row);
        });
        delete vals[""]; // cleanup
        vals['doses'] = this.doses;
        this.data = vals;
        this.add_confidence_intervals();
        this._switch_dose(0);
        new DRPlot(this, '#endpoint_plot').build_plot();
    },
    inject_doses: function(doses){
        // add dose-units into endpoint-representation
        this.doses = _.map(doses, function(v){
            return {
                "key": v.units_id.toString(),
                "units": v.units,
                "values": v.values.map(function(v2){return {dose: v2};})
            };
        });
        this._switch_dose(0);
    },
    setOELS: function(){
      // set NOEL, LOEL, FEL
      var fields = $('#id_NOEL, #id_LOEL, #id_FEL')
            .html("<option value=-999>&lt;None&gt;</option>");

      $('.doses').each(function(i, v){
          fields.append('<option value="{0}">{1}</option>'.printf(i, v.textContent));
      });

      $('#id_NOEL option[value="{0}"]'.printf(this.data.NOEL)).prop('selected', true);
      $('#id_LOEL option[value="{0}"]'.printf(this.data.LOEL)).prop('selected', true);
      $('#id_FEL option[value="{0}"]'.printf(this.data.FEL)).prop('selected', true);
    }
};
_.extend(EditEndpoint.prototype, Endpoint.prototype);


// EditEndpoint subclass with individual animal-data
var EditEndpointIAD = function(endpoint, eg_table, doses){
    Endpoint.call(this, endpoint); // call parent constructor
    this.eg_table = $(eg_table);
    this.n_change_flag = true;
    this.doses = doses;
    this.dose_groups = doses[0].values.length;

    var self = this;
    this.eg_table.find('.n_fields').on('change', function(){
        self.n_change_flag = true; self.update_endpoint_from_form();
    });
};
EditEndpointIAD.prototype = {
    build_submission: function(){
        endpoint_groups = EditEndpoint.prototype.build_eg_submission.apply(this);
        var submission = [];
        this.data.endpoint_group.forEach(function(v1, i1){
            v1.individual_responses.forEach(function(v2, i2){
                submission.push({dose_group_id: i1, response: v2});
            });
        });
        return {endpoint_group: endpoint_groups,
                iad: JSON.stringify(submission)};
    },
    update_endpoint_from_form: function(){
        var vals = { 'endpoint_group':[], 'doses': this.doses};
        $('#endpoint :input').each(function() {
            vals[this.name] = $(this).val();
        });
        vals['NOEL'] = $('#id_NOEL option:selected').val();
        vals['LOEL'] = $('#id_LOEL option:selected').val();
        vals['FEL'] = $('#id_FEL option:selected').val();

        //now endpoint-group data
        for(var i=0; i<this.dose_groups; i++){
            var row = {
                incidence: null,
                n: parseFloat($('#n_' + i).val()),
                dose: parseFloat($('#dose_' + i).text()),
                individual_responses: [],
                significance_level: parseFloat($('#significance_level_' + i).val()) || 0};

            // update individual animal-data
            for(var j=0; j<row.n; j++){
                row.individual_responses.push(parseFloat($('#response_d' + i + '_id' + j).val()) || null);
            }

            this._calculate_summary_stats(row.individual_responses, i);

            // recalculate statistics
            $.extend(row, {response: parseFloat($('#response_' + i).val()),
                           variance: parseFloat($('#variance_' + i).val())});
            vals['endpoint_group'].push(row);
        }

        delete vals[""]; // cleanup
        this.data = vals;
        this.add_confidence_intervals();
        this.build_form_representation();
    },
    _calculate_summary_stats: function(responses, i){
        var mean = Math.mean(responses),
            stdev = Math.stdev(responses);
        if((typeof mean === 'number') && (typeof stdev === 'number')){
            $('#resp_' + i).val(mean.toPrecision(5));
            $('#variance_' + i).val(stdev.toPrecision(5));
        } else {
            $('#resp_' + i).val("-");
            $('#variance_' + i).val("-");
        }
    },
    build_form_representation: function(){
        if (this.n_change_flag) this.build_iad_rows();
        this.change_dose_pulldowns();
        window.plot = new BWPlot(this, '#bmd_ds_plot');
        window.plot.build_plot();
    },
    change_dose_pulldowns: function(){
        EditEndpoint.prototype.change_dose_pulldowns.apply(this);
    },
    build_iad_rows: function(){
        var num_rows = d3.max(this.data.endpoint_group.map(function(v){return v.n;})) || 0,
            tbody = $('<tbody>');
        for(var i=0; i<num_rows; i++){
            var tr = $('<tr>').append($('<td>').text('ID {0}'.printf(i+1)));
            for(var j=0; j<this.dose_groups; j++){
                var td = $('<td>');
                if(this.data.endpoint_group[j].n>i){
                    td.html('<input tabindex="{0}" class="span12 response_fields" type="text" id="response_d{1}_id{2}" value="{3}">'
                            .printf(j+10,j,i,this.data.endpoint_group[j].individual_responses[i]));
                }
                tr.append(td);
            }
            tbody.append(tr);
        }
        this.eg_table.find('tbody').replaceWith(tbody);
        this.n_change_flag = false;
    },
    load_values_into_form: function(){
        // load values from object representation into form
        this.data.endpoint_group.forEach(function(v, i){
            $('#n_' + i).val(v.n);
            $('#inc_' + i).val(v.incidence);
            $('#resp_' + i).val(v.response);
            $('#variance_' + i).val(v.variance);
            $('#significance_level_' + i).val(v.significance_level ||'-');
        });
        this.build_iad_rows();
    }
};
_.extend(EditEndpointIAD.prototype, EditEndpoint.prototype);


// Widget to calculate if sample size is appropriate for measured results
var SampleSizeWidget = function(){
    this.btn = $('#ssBtn')
        .appendTo($("#hint_id_power_notes"))
        .click(this.setCalculator.bind(this));
    this.modal = $('#ssModal');
    this.form = $('#ssForm');
    this.result = this.form.find("#ssResult");
    this.form.find("input").on('change keyup', this.recalculate.bind(this));
    $('#ssSavePower').click(this.savePower.bind(this));
};
SampleSizeWidget.prototype = {
    getSD: function(){
        var n = $("#n_1").val(),
            varType = $("#id_variance_type").val(),
            variance = $("#variance_0").val(),
            val = NaN;

        switch(varType){
            case "1": //SD
                val = variance;
            case "2": //SE
                if ($.isNumeric(variance) && $.isNumeric(n)){
                    val =  Math.round(variance * Math.sqrt(n));
                }
        }
        return val;
    },
    setCalculator: function(){
        this.form.find("input[name=mean]").val( $("#resp_0").val() );
        this.form.find("input[name=sd]").val( this.getSD() );
        this.form.find("input[name=n]").val( $("#n_1").val() );
        this.recalculate();
    },
    recalculate: function(){
        var fields = _.object(_.map(this.form.serializeArray(), function(d){
                return [d.name, parseFloat(d.value, 10)]; })),
            txt = "Error in input fields.",
            power, ratio;
        if(!isNaN(fields.mean) && !isNaN(fields.sd) && !isNaN(fields.percentToDetect)){
            power = Math.round(this.getPower(fields.mean, fields.sd, fields.percentToDetect));

            if (!isNaN(fields.n)){
                ratio = fields.n/power;
                if (ratio <= 0.5){
                    txt = "underpowered (sample size is ≤50% required), ";
                } else if (ratio<1.0){
                    txt = "marginally underpowered (sample size is between 50-100% required), ";
                } else {
                    txt = "sufficiently powered (sample size ≥100% required), ";
                }
            } else {
                txt = "Effect ";
            }
            txt += "requires approximately {0} animals to detect a {1}% change from control at 80% power".printf(power, fields.percentToDetect);
        }
        return this.result.html(txt);
    },
    getPower: function(mean, sd, percentToDetect){
        // Calculate the sample size required to detect a response with 80%
        // power, which is dependent on the control mean and standard-deviation,
        // along with the fraction to detect such as a 10% (0.10) change from control
        var fracToDetect = percentToDetect/100,
            d = mean*fracToDetect/sd,
            ss80 = 16/Math.pow(d, 2);
        return ss80;
    },
    savePower: function(){
        $("#id_power_notes").html(this.result.html());
    }
};
