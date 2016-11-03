import _ from 'underscore';
import $ from '$';

import Reference from './Reference';
import ReferencesViewer from './ReferencesViewer';
import TagTree from './TagTree';


let startupSearchReference = function(assessment_id, tags, canEdit){
    window.assessment_pk = assessment_id;
    window.tagtree = new TagTree(tags);
    window.canEdit = canEdit;

    let refviewer = new ReferencesViewer($('#references_detail_div'), {fixed_title: 'Search Results'}),
        handleResults = function(results){
            if(results.status === 'success'){
                let refs = results.refs
                    .map((d) => new Reference(d, window.tagtree));
                refviewer.set_references(refs);
            } else {
                refviewer.set_error();
            }
        },
        print_search_fields = function(){
            $('#search_context').html(`<div>
                <p><b>Title: </b>${$('#id_title').val()}</p>
                <p><b>Authors: </b>${$('#id_authors').val()}</p>
                <p><b>Journal/Year: </b>${$('#id_journal').val()}</p>
                <p><b>Database ID: </b>${$('#id_db_id').val()}</p>
            </div>`);
        };

    $('#searchFormHolder > form').submit(function(event){
        event.preventDefault();
        print_search_fields();
        let data = $(this).serialize();
        $.post('.', data).done(handleResults);
        $('#resultsHolder').fadeIn();
        $('#searchFormHolder').fadeOut();
    });

    $('#search_again').click(function(){
        $('#resultsHolder').fadeOut();
        $('#searchFormHolder').fadeIn();
    });
};

export default startupSearchReference;
