var IVChemical = function(data){
    this.data = data;
};
_.extend(IVChemical, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/chemical/{0}/'.printf(id), function(d){
            cb(new IVChemical(d));
        });
    },
    displayAsModal: function(id){
        IVChemical.get_object(id, function(d){d.displayAsModal();});
    }
});
IVChemical.prototype = {
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr("Chemical name", this.data.name)
            .add_tbody_tr("CAS", this.data.cas)
            .add_tbody_tr("CAS inferred?", HAWCUtils.booleanCheckbox(this.data.cas_inferred))
            .add_tbody_tr("CAS notes", this.data.cas_notes)
            .add_tbody_tr("Source", this.data.source)
            .add_tbody_tr("Purity", this.data.purity)
            .add_tbody_tr("Purity confirmed?", HAWCUtils.booleanCheckbox(this.data.purity_confirmed))
            .add_tbody_tr("Purity notes", this.data.purity_confirmed_notes)
            .add_tbody_tr("Dilution/storage/precipitation notes", this.data.dilution_storage_notes)
            .get_tbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(d.data.name),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
};


var IVExperiment = function(data){
    this.data = data;
};
_.extend(IVExperiment, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/experiment/{0}/'.printf(id), function(d){
            cb(new IVExperiment(d));
        });
    },
    displayAsModal: function(id){
        IVExperiment.get_object(id, function(d){d.displayAsModal();});
    }
});
IVExperiment.prototype = {
    build_details_table: function(){
        var tbl = new DescriptiveTable();
        tbl.add_tbody_tr("Cell type", this.data.cell_type.cell_type);
        tbl.add_tbody_tr("Tissue", this.data.cell_type.tissue);
        tbl.add_tbody_tr("Species", this.data.cell_type.species);
        tbl.add_tbody_tr("Sex", this.data.cell_type.sex_symbol);
        tbl.add_tbody_tr("Cell source", this.data.cell_type.source);
        tbl.add_tbody_tr("Transfection", this.data.transfection);
        tbl.add_tbody_tr("Cell line", this.data.cell_line);
        tbl.add_tbody_tr("Dosing notes", this.data.dosing_notes);
        tbl.add_tbody_tr("Metabolic activation", this.data.metabolic_activation);
        tbl.add_tbody_tr("Serum", this.data.serum);
        tbl.add_tbody_tr("Has positive control", this.data.has_positive_control);
        tbl.add_tbody_tr("Positive control", this.data.positive_control);
        tbl.add_tbody_tr("Has negative control", this.data.has_negative_control);
        tbl.add_tbody_tr("Negative control", this.data.negative_control);
        tbl.add_tbody_tr("Has vehicle control", this.data.has_vehicle_control);
        tbl.add_tbody_tr("Vehicle control", this.data.vehicle_control);
        tbl.add_tbody_tr("Control notes", this.data.control_notes);
        tbl.add_tbody_tr("Dose units", this.data.dose_units.units);
        return tbl.get_tbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf("Experimental details"),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
};


var IVEndpoint = function(data){
    this.data = data;
    this._build_ivegs();
};
_.extend(IVEndpoint, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/endpoint/{0}/'.printf(id), function(d){
            cb(new IVEndpoint(d));
        });
    },
    displayAsModal: function(id){
        IVEndpoint.get_object(id, function(d){d.displayAsModal();});
    }
});
IVEndpoint.prototype = {
    _build_ivegs: function(){
        var groups = this.data.groups;
        groups.sort(function(a, b){ return a.id - b.id;});
        this.egs = groups.map(function(v){return new IVEndpointGroup(v);});
        delete this.data.groups;
    }, build_details_table: function(){

        var self = this,
            tbl = new DescriptiveTable(),
            getBenchmarkText = function(d){
                return "{0}: {1}".printf(d.benchmark, d.value);
            }, getCriticalValue = function(idx){
                try{
                    return "{0} {1}".printf(self.egs[idx].data.dose, self.data.experiment.dose_units.units);
                }catch(err){
                    return undefined;
                }
            }, getObservationTime = function(){
                if (self.data.observation_time>=0)
                    return "{0} {1}".printf(self.data.observation_time, self.data.observation_time_units);
            };

        tbl.add_tbody_tr("Name", this.data.name);
        tbl.add_tbody_tr("Assay type", this.data.assay_type);
        tbl.add_tbody_tr("Short description", this.data.short_description);
        tbl.add_tbody_tr("Data location", this.data.data_location);
        tbl.add_tbody_tr("Data type", this.data.data_type);
        tbl.add_tbody_tr("Variance type", this.data.variance_type);
        tbl.add_tbody_tr("Response units", this.data.response_units);
        tbl.add_tbody_tr("Observation time", getObservationTime());
        tbl.add_tbody_tr("NOAEL", getCriticalValue(this.data.NOAEL));
        tbl.add_tbody_tr("LOAEL", getCriticalValue(this.data.LOAEL));
        tbl.add_tbody_tr("Monotonicity", this.data.monotonicity);
        tbl.add_tbody_tr("Overall pattern", this.data.overall_pattern);
        tbl.add_tbody_tr("Statistical test notes", this.data.statistical_test_notes);
        tbl.add_tbody_tr("Trend test", this.data.trend_test);
        tbl.add_tbody_tr("Endpoint notes", this.data.endpoint_notes);
        tbl.add_tbody_tr("Result notes", this.data.result_notes);
        tbl.add_tbody_tr("Category", this.data.category.name);
        tbl.add_tbody_tr_list("Effects", _.pluck(this.data.effects, "name"));
        tbl.add_tbody_tr_list("Benchmarks", this.data.benchmarks.map(getBenchmarkText));

        // add additional fields
        _.map(this.data.additional_fields, function(val, key){
            tbl.add_tbody_tr(HAWCUtils.prettifyVariableName(key), val);
        });

        return tbl.get_tbl();
    }, build_eg_table: function(){
        var self = this,
            tbl = new BaseTable(),
            opts = {},
            getAvailableColumns = function(){
                var opts = {
                    hasN: false,
                    hasResponse: false,
                    hasVariance: false,
                    hasDiffControl: false,
                    hasSigControl: false,
                    hasCytotox: false
                }
                self.egs.forEach(function(v){
                    if (v.data.n !== null) opts.hasN = true;
                    if (v.data.response !== null) opts.hasResponse = true;
                    if (v.data.variance !== null) opts.hasVariance = true;
                    if (v.data.difference_control !== "not-tested") opts.hasDiffControl = true;
                    if (v.data.significant_control !== "not reported") opts.hasSigControl = true;
                    if (v.data.cytotoxicity_observed !== "not reported") opts.hasCytotox = true;
                });
                return opts;
            }, opts = getAvailableColumns(),
            headers = function(opts){
                var arr = ["Dose"];
                if (opts.hasN) arr.push("N");
                if (opts.hasResponse) arr.push("Response");
                if (opts.hasVariance) arr.push("Variance");
                if (opts.hasDiffControl) arr.push("Difference<br>Control");
                if (opts.hasSigControl) arr.push("Significant<br>Control");
                if (opts.hasCytotox) arr.push("Cytotoxicity<br>Observed");
                return arr;
            };

        tbl.addHeaderRow(headers(opts));
        this.egs.forEach(function(v, i){
            opts.isLOAEL = (i === self.data.LOAEL);
            opts.isLOAEL = (i === self.data.NOAEL);
            tbl.addRow(v.build_row(tbl, opts));
        });
        return tbl.getTbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(d.data.name),
            $details = $('<div class="span12">'),
            $eg_tbl = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details))
                .append($('<div class="row-fluid">').append($eg_tbl));

        $details.append(this.build_details_table());
        $eg_tbl.append(this.build_eg_table());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
};


var IVEndpointGroup = function(data){
    this.data = data;
};
IVEndpointGroup.prototype = {
    build_row: function(tbl, opts){
        var tr = $('<tr>'),
            getDose = function(dose){
                var txt = dose;
                if(opts.isNOAEL)
                    txt += tbl.footnotes.add_footnote('NOAEL (No Observed Adverse Effect Level)');
                if(opts.isLOAEL)
                    txt += tbl.footnotes.add_footnote('LOAEL (Lowest Observed Adverse Effect Level)');
                return txt;
            };

        tr.append('<td>{0}</td>'.printf(getDose(this.data.dose)))

        if (opts.hasN)
            tr.append('<td>{0}</td>'.printf(this.data.n));

        if (opts.hasResponse)
            tr.append('<td>{0}</td>'.printf(this.data.response));

        if (opts.hasVariance)
            tr.append('<td>{0}</td>'.printf(this.data.variance));

        if (opts.hasDiffControl)
            tr.append('<td>{0}</td>'.printf(this.data.difference_control));

        if (opts.hasSigControl)
            tr.append('<td>{0}</td>'.printf(this.data.significant_control));

        if (opts.hasCytotox)
            tr.append('<td>{0}</td>'.printf(this.data.cytotoxicity_observed));

        return tr;
    }
};
