import BaseTable from 'utils/BaseTable';

class IVEndpointListTable {
    constructor(endpoints) {
        this.endpoints = endpoints;
        this.table = new BaseTable();
    }

    buildTable() {
        if (this.endpoints.length === 0) {
            return '<p>No endpoints available.</p>';
        }

        var table = this.table,
            headers = [
                'Study',
                'Experiment',
                'Chemical',
                'Endpoint',
                'Effect Category',
                'Effects',
                'Dose Units',
                'Response Units',
            ];
        table.setColGroup([10, 16, 12, 11, 16, 20, 7, 7]);
        table.addHeaderRow(headers);
        this.endpoints.map(endpoint => {
            table.addRow(endpoint.buildListRow());
        });
        return table.getTbl();
    }
}

export default IVEndpointListTable;
