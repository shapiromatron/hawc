import React from 'react';

import './Tree.css';
import Node from '../components/Node';


class Tree extends React.Component {

    render() {
        let nodes =  this.props.nodes;
        return (
            <div>
                <h1>
                    Modify in-vitro endpoint categories
                    <button className="pull-right btn btn-primary">Add new category</button>
                </h1>
                {nodes.map(function(d){
                    return <Node key={d.id} node={d} />;
                })}
            </div>
        );
    }
}

Tree.propTypes = {
    nodes: React.PropTypes.array.isRequired,
};

export default Tree;
