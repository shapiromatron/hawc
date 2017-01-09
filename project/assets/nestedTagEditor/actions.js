import fetch from 'isomorphic-fetch';
import _ from 'underscore';

import h from 'shared/utils/helpers';
import * as types from 'nestedTagEditor/constants';

import {
    NO_PARENT,
} from 'nestedTagEditor/constants';

var addDepth = function(node, depth){
        // add depth to each node, and recursively to child nodes
        node.data.depth = depth;

        if (node.children){
            node.children.forEach((d) => addDepth(d, depth+1));
        }
    },
    getOptions = function(nodes){
        let opts = [],
            addOption = function(node){
                let indentedName =  _.times(node.data.depth, (d) => ' _ ').join('') + node.data.name;
                opts.push([node.id, indentedName]);
                if (node.children){
                    node.children.forEach(addOption);
                }
            };

        nodes.forEach(addOption);
        opts.unshift([NO_PARENT, '---']);
        return opts;
    },
    receiveTags = function(allTags){
        let tags = allTags[0].children || [];
        tags.forEach((d) => addDepth(d, 0));
        return {
            type: types.RECEIVE_TAGLIST,
            tags,
            parentOptions: getOptions(tags),
        };
    },
    getTags = function(){
        return (dispatch, getState) => {
            const url = getState().config.list_url;

            return fetch(url, h.fetchGet)
                .then((response) => response.json())
                .then((json) => dispatch(receiveTags(json)))
                .catch((ex) => console.error('Tag parsing failed', ex));
        };
    },
    createTag = function(newNode){
        return (dispatch, getState) => {
            let state = getState(),
                url = `${state.config.base_url}`,
                csrf = state.config.csrf,
                obj = {
                    assessment_id: state.config.assessment_id,
                    name: newNode.name,
                    parent: newNode.parent,
                };

            return fetch(url, h.fetchPost(csrf, obj, 'POST'))
                .then((response) => {
                    if (response.ok){
                        return dispatch(getTags());
                    }
                })
                .catch((ex) => console.error('Tag patch failed', ex));
        };
    },
    updateTag = function(id, newNode){
        return (dispatch, getState) => {
            let state = getState(),
                url = `${state.config.base_url}${id}/`,
                csrf = state.config.csrf,
                obj = {
                    name: newNode.name,
                    parent: newNode.parent,
                };

            return fetch(url, h.fetchPost(csrf, obj, 'PATCH'))
                .then((response) => response.json())
                .then((json) => dispatch(getTags()))
                .catch((ex) => console.error('Tag patch failed', ex));
        };
    },
    deleteTag = function(id){
        return (dispatch, getState) => {
            let state = getState(),
                url = `${state.config.base_url}${id}/`,
                csrf = state.config.csrf;

            return fetch(url, h.fetchDelete(csrf))
                .then((response) => {
                    if (response.ok){
                        return dispatch(getTags());
                    }
                })
                .catch((ex) => console.error('Tag delete failed', ex));
        };
    },
    moveTag = function(nodeId, oldIndex, newIndex){
        return (dispatch, getState) => {
            let state = getState(),
                url = `${state.config.base_url}${nodeId}/move/`,
                csrf = state.config.csrf,
                obj = {
                    oldIndex,
                    newIndex,
                };

            return fetch(url, h.fetchPost(csrf, obj, 'PATCH'))
                .then((response) => response.json())
                .then((json) => dispatch(getTags()))
                .catch((ex) => console.error('Tag patch failed', ex));
        };
    };

export { getTags };
export { createTag };
export { updateTag };
export { deleteTag };
export { moveTag };
