import fetch from 'isomorphic-fetch';

import h from 'textCleanup/utils/helpers';
import * as types from 'ivEndpointCategories/constants';


var addDepth = function(node, depth){
        // add depth to each node, and recursively to child nodes
        node.data.depth = depth;

        if (node.children){
            node.children.forEach((d) => addDepth(d, depth+1));
        }
    },
    receiveTags = function(allTags){
        let tags = allTags[0].children || [];
        tags.forEach((d) => addDepth(d, 0));
        return {
            type: types.RECEIVE_TAGLIST,
            tags,
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
    createTag = function(){
        return (dispatch, getState) => {
            console.log('create me!')
            return null;
        };
    },
    updateTag = function(id, name){
        return (dispatch, getState) => {
            let state = getState(),
                url = `${state.config.base_url}${id}/`,
                csrf = state.config.csrf,
                obj = {name};

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
    };

export { getTags };
export { createTag };
export { updateTag };
export { deleteTag };
