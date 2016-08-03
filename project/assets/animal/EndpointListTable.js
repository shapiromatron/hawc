var EndpointListTable = function(endpoints, dose_id){
    if(dose_id) _.each(endpoints, function(e){e.switch_dose_units(dose_id);});
    this.endpoints = endpoints;
    this.tbl = new BaseTable();
};

EndpointListTable.prototype = {
    build_table(){

        if(this.endpoints.length === 0)
            return '<p>No endpoints available.</p>';

        var tbl = this.tbl,
            headers = [
                'Study',
                'Experiment',
                'Animal Group',
                'Endpoint',
                'Units',
                'NOEL',
                'LOEL',
            ];
        tbl.setColGroup([12, 16, 17, 31, 10, 7, 7]);
        tbl.addHeaderRow(headers);
        this.endpoints.forEach(function(v){
            tbl.addRow(v.build_endpoint_list_row());
        });
        return tbl.getTbl();
    },
};

export default EndpointListTable;
