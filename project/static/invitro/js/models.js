/* eslint object-shorthand: "off" */

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
    },
    displayAsPage: function(id, div){
        IVChemical.get_object(id, function(d){d.displayAsPage(div);});
    },
});
IVChemical.prototype = {
    build_title: function(){
        var el = $('<h1>').text(this.data.name);
        if (window.canEdit){
            var urls = [
                'Chemical editing',
                {url: this.data.url_update, text: 'Update'},
                {url: this.data.url_delete, text: 'Delete'},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    },
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr('Chemical name', this.data.name)
            .add_tbody_tr('CAS', this.data.cas)
            .add_tbody_tr('CAS inferred?', HAWCUtils.booleanCheckbox(this.data.cas_inferred))
            .add_tbody_tr('CAS notes', this.data.cas_notes)
            .add_tbody_tr('Source', this.data.source)
            .add_tbody_tr('Purity', this.data.purity)
            .add_tbody_tr('Purity confirmed?', HAWCUtils.booleanCheckbox(this.data.purity_confirmed))
            .add_tbody_tr('Purity notes', this.data.purity_confirmed_notes)
            .add_tbody_tr('Dilution/storage/precipitation notes', this.data.dilution_storage_notes)
            .get_tbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.data.name),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    },
    displayAsPage: function($div){
        $div
            .append(this.build_title())
            .append(this.build_details_table());
    },
};


var IVCellType = function(data){
    this.data = data;
};
_.extend(IVCellType, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/celltype/{0}/'.printf(id), function(d){
            cb(new IVCellType(d));
        });
    },
    displayAsModal: function(id){
        IVCellType.get_object(id, function(d){d.displayAsModal();});
    },
    displayAsPage: function(id, div){
        IVCellType.get_object(id, function(d){d.displayAsPage(div);});
    },
});
IVCellType.prototype = {
    build_title: function(){
        var el = $('<h1>').text(this.data.title);
        if (window.canEdit){
            var urls = [
                'Cell type editing',
                {url: this.data.url_update, text: 'Update'},
                {url: this.data.url_delete, text: 'Delete'},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    },
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr('Cell type', this.data.cell_type)
            .add_tbody_tr('Tissue', this.data.tissue)
            .add_tbody_tr('Species', this.data.species)
            .add_tbody_tr('Strain', this.data.strain)
            .add_tbody_tr('Sex', this.data.sex_symbol)
            .add_tbody_tr('Cell source', this.data.source)
            .add_tbody_tr('Culture type', this.data.culture_type)
            .get_tbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.data.name),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    },
    displayAsPage: function($div){
        $div
            .append(this.build_title())
            .append(this.build_details_table());
    },
};


var IVExperiment = function(data){
    this.data = data;
    this.initEndpoints();
};
_.extend(IVExperiment, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/experiment/{0}/'.printf(id), function(d){
            cb(new IVExperiment(d));
        });
    },
    displayAsModal: function(id){
        IVExperiment.get_object(id, function(d){d.displayAsModal();});
    },
    displayAsPage: function(id, div){
        IVExperiment.get_object(id, function(d){d.displayAsPage(div);});
    },
});
IVExperiment.prototype = {
    initEndpoints: function(){
        this.endpoints = [];
        if(this.data.endpoints){
            this.endpoints = _.map(
               this.data.endpoints,
               function(d){return new IVEndpoint(d);});
            delete this.data.endpoints;
        }
    },
    build_title: function(){
        var el = $('<h1>').text(this.data.name);
        if (window.canEdit){
            var urls = [
                'Experiment editing',
                {url: this.data.url_update, text: 'Update'},
                {url: this.data.url_delete, text: 'Delete'},
                'Endpoint editing',
                {url: this.data.url_create_endpoint, text: 'Create endpoint'},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    },
    build_details_table: function(){
        var getControlText = function(bool, str) {
                var txt = HAWCUtils.booleanCheckbox(bool);
                if (bool && str) txt = str;
                return txt;
            },
            pos = getControlText(this.data.has_positive_control, this.data.positive_control),
            neg = getControlText(this.data.has_negative_control, this.data.negative_control),
            veh = getControlText(this.data.has_vehicle_control, this.data.vehicle_control),
            naive = getControlText(this.data.has_naive_control, '');

        return new DescriptiveTable()
            .add_tbody_tr('Cell type', this.data.cell_type.cell_type)
            .add_tbody_tr('Tissue', this.data.cell_type.tissue)
            .add_tbody_tr('Species', this.data.cell_type.species)
            .add_tbody_tr('Strain', this.data.cell_type.strain)
            .add_tbody_tr('Sex', this.data.cell_type.sex_symbol)
            .add_tbody_tr('Cell source', this.data.cell_type.source)
            .add_tbody_tr('Culture type', this.data.cell_type.culture_type)
            .add_tbody_tr('Transfection', this.data.transfection)
            .add_tbody_tr('Cell notes', this.data.cell_notes)
            .add_tbody_tr('Dosing notes', this.data.dosing_notes)
            .add_tbody_tr('Metabolic activation', this.data.metabolic_activation)
            .add_tbody_tr('Serum', this.data.serum)
            .add_tbody_tr('Naive control', naive)
            .add_tbody_tr('Positive control', pos)
            .add_tbody_tr('Negative control', neg)
            .add_tbody_tr('Vehicle control', veh)
            .add_tbody_tr('Control notes', this.data.control_notes)
            .add_tbody_tr('Dose units', this.data.dose_units.name)
            .get_tbl();
    },
    build_endpoint_list: function(){
        var ul = $('<ul>');

        if (this.endpoints.length===0){
            ul.append('<li><i>No endpoints available.</i></li>');
        }

        this.endpoints.forEach(function(d){
            ul.append($('<li>').html(d.build_hyperlink()));
        });

        return ul;
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf('Experimental details'),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    },
    displayAsPage: function($div){
        $div
            .append(this.build_title())
            .append(this.build_details_table())
            .append('<h2>Available endpoints</h2>')
            .append(this.build_endpoint_list());
    },
};


var IVEndpoint = function(data){
    this.data = data;
    this._build_ivegs();
    this._build_chemical();
};
_.extend(IVEndpoint, {
    get_object: function(id, cb){
        $.get('/in-vitro/api/endpoint/{0}/'.printf(id), function(d){
            cb(new IVEndpoint(d));
        });
    },
    displayAsModal: function(id){
        IVEndpoint.get_object(id, function(d){d.displayAsModal();});
    },
    displayAsPage: function(id, div){
        IVEndpoint.get_object(id, function(d){d.displayAsPage(div);});
    },
});
IVEndpoint.prototype = {
    _build_ivegs: function(){
        var groups = this.data.groups;
        groups.sort(function(a, b){ return a.id - b.id;});
        this.egs = groups.map(function(v){return new IVEndpointGroup(v);});
        delete this.data.groups;
    },
    _build_chemical: function(){
        if (this.data.chemical){
            this.chemical = new IVChemical(this.data.chemical);
            delete this.data.chemical;
        }
    },
    build_hyperlink: function(){
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this._title_text());
    },
    _title_text: function(){
        return this.data.name;
    },
    build_title: function(){
        var el = $('<h1>').text(this._title_text());
        if (window.canEdit){
            var urls = [
                'Endpoint editing',
                {url: this.data.url_update, text: 'Update'},
                {url: this.data.url_delete, text: 'Delete'},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    },
    build_details_table: function(){

        var self = this,
            tbl = new DescriptiveTable(),
            getBenchmarkText = function(d){
                return '{0}: {1}'.printf(d.benchmark, d.value);
            }, getCriticalValue = function(idx){
                try{
                    return '{0} {1}'.printf(self.egs[idx].data.dose, self.data.experiment.dose_units.name);
                }catch(err){
                    return undefined;
                }
            }, getObservationTime = function(){
                if (self.data.observation_time.length > 0)
                    return '{0} {1}'.printf(self.data.observation_time, self.data.observation_time_units);
            }, getCategory = function(cat){
                if (cat) return cat.names.join('→');
            };

        tbl.add_tbody_tr('Name', this.data.name)
           .add_tbody_tr('Assay type', this.data.assay_type)
           .add_tbody_tr('Short description', this.data.short_description)
           .add_tbody_tr('Effect category', this.data.effect)
           .add_tbody_tr('Specific category', getCategory(this.data.category))
           .add_tbody_tr('Data location', this.data.data_location)
           .add_tbody_tr('Data type', this.data.data_type)
           .add_tbody_tr('Variance type', this.data.variance_type)
           .add_tbody_tr('Response units', this.data.response_units)
           .add_tbody_tr('Values estimated', HAWCUtils.booleanCheckbox(this.data.values_estimated))
           .add_tbody_tr('Observation time', getObservationTime())
           .add_tbody_tr('NOEL', getCriticalValue(this.data.NOEL))
           .add_tbody_tr('LOEL', getCriticalValue(this.data.LOEL))
           .add_tbody_tr('Monotonicity', this.data.monotonicity)
           .add_tbody_tr('Overall pattern', this.data.overall_pattern)
           .add_tbody_tr('Statistical test notes', this.data.statistical_test_notes)
           .add_tbody_tr('Trend test', this.data.trend_test)
           .add_tbody_tr('Trend test notes', this.data.trend_test_notes)
           .add_tbody_tr('Endpoint notes', this.data.endpoint_notes)
           .add_tbody_tr('Result notes', this.data.result_notes)
           .add_tbody_tr_list('Effects', _.pluck(this.data.effects, 'name'))
           .add_tbody_tr_list('Benchmarks', this.data.benchmarks.map(getBenchmarkText));

        // add additional fields
        _.each(this.data.additional_fields, function(val, key){
            tbl.add_tbody_tr(HAWCUtils.prettifyVariableName(key), val);
        });

        return tbl.get_tbl();
    },
    build_eg_table: function(){
        var self = this,
            tbl = new BaseTable(),
            units = this.data.experiment.dose_units.name,
            getAvailableColumns = function(){
                var opts = {
                    hasN: false,
                    hasResponse: false,
                    hasVariance: false,
                    hasDiffControl: false,
                    hasSigControl: false,
                    hasCytotox: false,
                    hasPrecip: false,
                };
                self.egs.forEach(function(v){
                    if (v.data.n !== null) opts.hasN = true;
                    if (v.data.response !== null) opts.hasResponse = true;
                    if (v.data.variance !== null) opts.hasVariance = true;
                    if (v.data.difference_control !== 'not-tested') opts.hasDiffControl = true;
                    if (v.data.significant_control !== 'not reported') opts.hasSigControl = true;
                    if (v.data.cytotoxicity_observed !== 'not reported') opts.hasCytotox = true;
                    if (v.data.precipitation_observed !== 'not reported') opts.hasPrecip = true;
                });
                return opts;
            },
            opts = getAvailableColumns(),
            headers = function(opts){
                var arr = ['Dose ({0})'.printf(units)];
                if (opts.hasN) arr.push('N');
                if (opts.hasResponse) arr.push('Response');
                if (opts.hasVariance) arr.push('Variance');
                if (opts.hasDiffControl) arr.push('Difference<br>Control');
                if (opts.hasSigControl) arr.push('Significant<br>Control');
                if (opts.hasCytotox) arr.push('Cytotoxicity<br>Observed');
                if (opts.hasPrecip) arr.push('Precipitation<br>Observed');
                return arr;
            };

        tbl.addHeaderRow(headers(opts));
        this.egs.forEach(function(v, i){
            opts.isLOEL = (i === self.data.LOEL);
            opts.isNOEL = (i === self.data.NOEL);
            tbl.addRow(v.build_row(tbl, opts));
        });
        return tbl.getTbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4><a href="{0}">{1}</a></h4>'.printf(this.data.url, this.data.name),
            $details = $('<div class="span12">'),
            $eg_tbl = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details))
                .append($('<div class="row-fluid">').append($eg_tbl));

        $details.append(this.build_details_table());
        $eg_tbl.append(this.build_eg_table());

        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    },
    displayAsPage: function($div){
        $div
            .append(this.build_title())
            .append(this.build_details_table())
            .append('<h2>Chemical details</h2>')
            .append(this.chemical.build_details_table())
            .append('<h2>Endpoint-group</h2>')
            .append(this.build_eg_table());
    },
};


var IVEndpointGroup = function(data){
    this.data = data;
};
IVEndpointGroup.prototype = {
    build_row: function(tbl, opts){
        var tr = $('<tr>'),
            getDose = function(dose){
                var txt = dose;
                if(opts.isNOEL)
                    txt += tbl.footnotes.add_footnote('NOEL (No Observed Effect Level)');
                if(opts.isLOEL)
                    txt += tbl.footnotes.add_footnote('LOEL (Lowest Observed Effect Level)');
                return txt;
            },
            getNumeric = function(val){
                return ($.isNumeric(val)) ? val.toLocaleString() : '-';
            };

        tr.append('<td>{0}</td>'.printf(getDose(this.data.dose)));

        if (opts.hasN)
            tr.append('<td>{0}</td>'.printf(getNumeric(this.data.n)));

        if (opts.hasResponse)
            tr.append('<td>{0}</td>'.printf(getNumeric(this.data.response)));

        if (opts.hasVariance)
            tr.append('<td>{0}</td>'.printf(getNumeric(this.data.variance)));

        if (opts.hasDiffControl)
            tr.append('<td>{0}</td>'.printf(this.data.difference_control));

        if (opts.hasSigControl)
            tr.append('<td>{0}</td>'.printf(this.data.significant_control));

        if (opts.hasCytotox)
            tr.append('<td>{0}</td>'.printf(this.data.cytotoxicity_observed));

        if (opts.hasPrecip)
            tr.append('<td>{0}</td>'.printf(this.data.precipitation_observed));

        return tr;
    },
};
