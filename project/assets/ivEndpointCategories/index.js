import React from 'react';
import { render } from 'react-dom';

import Tree from './containers/Tree';


let setDepth = function(node, depth){
    node.data.depth = depth;
    if (node.children){
        node.children.forEach(function(d){setDepth(d, depth+1);});
    }
};

const startup = function(data){
    data.forEach(function(d){setDepth(d, 0);});
    render(
       <Tree nodes={data}/>,
       document.getElementById('root')
    );
};

export default startup;
