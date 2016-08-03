// Widget to calculate if sample size is appropriate for measured results
var SampleSizeWidget = function(){
    this.btn = $('#ssBtn')
        .appendTo($('#hint_id_power_notes'))
        .click(this.setCalculator.bind(this));
    this.modal = $('#ssModal');
    this.form = $('#ssForm');
    this.result = this.form.find('#ssResult');
    this.form.find('input').on('change keyup', this.recalculate.bind(this));
    $('#ssSavePower').click(this.savePower.bind(this));
};
SampleSizeWidget.prototype = {
    getSD(){
        var n = $('#id_form-0-n').val(),
            varType = $('#id_variance_type').val(),
            variance = $('#id_form-0-variance').val(),
            val = NaN;

        switch(varType){
        case '1': //SD
            val = variance;
            break;
        case '2': //SE
            if ($.isNumeric(variance) && $.isNumeric(n)){
                val =  Math.round(variance * Math.sqrt(n));
            }
        }
        return val;
    },
    setCalculator(){
        this.form.find('input[name=mean]').val( $('#id_form-0-response').val() );
        this.form.find('input[name=sd]').val( this.getSD() );
        this.form.find('input[name=n]').val( $('#id_form-0-n').val() );
        this.recalculate();
    },
    recalculate(){
        var fields = _.object(_.map(this.form.serializeArray(), function(d){
                return [d.name, parseFloat(d.value, 10)]; })),
            txt = 'Error in input fields.',
            power, ratio;
        if(!isNaN(fields.mean) && !isNaN(fields.sd) && !isNaN(fields.percentToDetect)){
            power = Math.round(this.getPower(fields.mean, fields.sd, fields.percentToDetect));

            if (!isNaN(fields.n)){
                ratio = fields.n/power;
                if (ratio <= 0.5){
                    txt = 'underpowered (sample size is ≤50% required), ';
                } else if (ratio<1.0){
                    txt = 'marginally underpowered (sample size is between 50-100% required), ';
                } else {
                    txt = 'sufficiently powered (sample size ≥100% required), ';
                }
            } else {
                txt = 'Effect ';
            }
            txt += 'requires approximately {0} animals to detect a {1}% change from control at 80% power'.printf(power, fields.percentToDetect);
        }
        return this.result.html(txt);
    },
    getPower(mean, sd, percentToDetect){
        // Calculate the sample size required to detect a response with 80%
        // power, which is dependent on the control mean and standard-deviation,
        // along with the fraction to detect such as a 10% (0.10) change from control
        var fracToDetect = percentToDetect/100,
            d = mean*fracToDetect/sd,
            ss80 = 16/Math.pow(d, 2);
        return ss80;
    },
    savePower(){
        $('#id_power_notes').html(this.result.html());
    },
};

export default SampleSizeWidget;
