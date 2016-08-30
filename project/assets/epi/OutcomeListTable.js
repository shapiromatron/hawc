import BaseTable from 'utils/BaseTable';

class OutcomeListTable {

    constructor(outcomes) {
        this.outcomes = outcomes;
        this.table = new BaseTable();
    }

    buildTable() {
        if (this.outcomes.length === 0) {
            return '<p>No endpoints available.</p>';
        }

        var table = this.table,
            headers = [
                'Study',
                'Study population',
                'Outcome',
                'System',
                'Effect',
                'Diagnostic',
            ];
        table.setColGroup([12, 25, 16, 17, 10, 13]);
        table.addHeaderRow(headers);
        this.outcomes.map((outcome) => {
            table.addRow(outcome.buildListRow());
        });
        return table.getTbl();
    }
}

export default OutcomeListTable;