import fetch from 'isomorphic-fetch';

import h from 'textCleanup/utils/helpers';
import * as types from 'ivEndpointCategories/constants';



var receiveTags = function(allTags){
        let tags = allTags[0].children || [];
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
    };

export { getTags };
