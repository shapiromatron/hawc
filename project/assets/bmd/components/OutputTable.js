import React from 'react';


class OutputTable extends React.Component {

    render() {
        return (
            <div>
                <h3>BMDS output summary</h3>
                <div className="row-fluid">

                    <div className='span8'>
                        <table className="table table-condensed">
                            <thead>
                            </thead>
                            <tfoot>
                                <tr>
                                    <td colSpan="100">
                                        Selected model highlighted in yellow
                                    </td>
                                </tr>
                            </tfoot>
                            <tbody>
                            </tbody>
                        </table>
                    </div>

                    <div className='d3_container span4'>
                    </div>

                </div>
            </div>
        );
    }
}

OutputTable.propTypes = {
};

export default OutputTable;
