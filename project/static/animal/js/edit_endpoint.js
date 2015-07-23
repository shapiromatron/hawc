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
        var vals = { 'groups': [] };
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
            vals.groups.push(row);
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
