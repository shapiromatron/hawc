import React { Component, PropTypes } from 'react';

class ModelList extends Component{
    renderModelItem(item){
        return (
            <li key={item}>
                <a href={item.url}>{item.length} {item.name}s</a>
            </li>
        )
    }
    render(){
        const isEmpty = items.length === 0
        if(isEmpty){
            return <li><i>No endpoints are available for this {model}.</i></li>

        }
        return (
            <h1>{model} Results for Cleanup</h1>
            <ul>
                {items.map(renderModelItem)}
            </ul>
        )
    }
