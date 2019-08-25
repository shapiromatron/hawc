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

        var headersToSortKeys = table.makeHeaderToSortKeyMapFromOrderByDropdown(
            'select#id_order_by',
            {
                'experiment name': 'experiment',
                'endpoint name': 'endpoint',
                effect: 'effect category',
            }
        );

        table.enableSortableHeaderLinks($('#initial_order_by').val(), headersToSortKeys, {
            unsortableColumns: ['effects'],
        });

        this.endpoints.map((endpoint) => {
            table.addRow(endpoint.buildListRow());
        });
        return table.getTbl();
    }
}

export default IVEndpointListTable;
