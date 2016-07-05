import React from 'react';
import ReactDOM from 'react-dom';

import DomainCell from 'robTable/components/DomainCell';
import './AggregateGraph.css';


const AggregateGraph = (props) => {
    return (
        <div className='aggregate-graph'>
            <div className='aggregate-flex'>

                {_.map(props.domains, (domain) => {
                    return <DomainCell key={domain.key}
                               domain={domain}
                               handleClick={props.handleClick}
                               />;
                })}
            </div>
            <div className='footer muted'>
                Click on any cell above to view details.
            </div>
        </div>
    );
};

export function renderAggregateGraph(data, element){
    ReactDOM.render(<AggregateGraph domains={data.domains} handleClick={data.handleClick} />, element);
}

export default AggregateGraph;
