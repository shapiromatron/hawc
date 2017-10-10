class EndpointCriticalDose {
    constructor(endpoint, span, type, show_units){
        // custom field to observe dose changes and respond based on selected dose
        endpoint.addObserver(this);
        this.endpoint = endpoint;
        this.span = span;
        this.type = type;
        this.critical_effect_idx = endpoint.data[type];
        this.show_units = show_units;
        this.display();
    }

    display(){
        var txt = '',
            self = this,
            doses = this.endpoint.doses.filter(function(v){
                return v.name === self.endpoint.dose_units;});
        try {
            txt = doses[0].values[this.critical_effect_idx].dose.toHawcString();
            if (this.show_units) txt = '{0} {1}'.printf(txt, this.endpoint.dose_units);
        } catch(err){
            console.log('dose units not found');
        }
        this.span.html(txt);
    }

    update(){
        this.display();
    }
}

export default EndpointCriticalDose;
