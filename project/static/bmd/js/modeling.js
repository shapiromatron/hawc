$(document).ready(function () {

    //Tab changes
        $('.nav-tabs a').click(function (e) {
          e.preventDefault();
          $(this).tab('show');
          bmd_ds_plot.build_plot();
          bmd_output_plot.build_plot();
        });

    //BMD settings - Options
        $("#bmd_setup_tbl").on('click', '.bmd_edit', function(e){
            e.preventDefault();
            $('#bmd_settings_form').modal({
                    backdrop: true,
                    keyboard: true
                });
            var td_details = $(this).parent().prev();
            if (crud =='Read'){
                $(this).parent().parent().data('bmd_option').build_settings_tbl(td_details);
            } else {
                $(this).parent().parent().data('bmd_option').build_settings_form(td_details);
            }
        });

        $('#bmds_options_new').click(function(e){
            //get new setup from ajax request, append to table
            e.preventDefault();
            var model = $('#bmds_options_select > option:selected').text();
            load_option_file(model, '#bmd_setup_tbl tbody');
        });

        $("#bmd_settings_save").click(function(){
            if ($('#bmd_settings_form').data('opt').save()) {
                $('#bmd_settings_form').modal('toggle');
            }
        });

        $("#bmd_settings_close").click(function(){
            $('#bmd_settings_form').modal('toggle');
        });

        $("#bmd_settings_delete").click(function(){
            $('#bmd_settings_form').data('opt').option_delete();
        });

        $("#bmd_settings_default").click(function(){
            $('#bmd_settings_form').data('opt').reset();
        });

        $("#bmd_settings_form").on("change", ".inp_selector", function(e){
            if ($(this).find("option:selected").val() == 'd') {
                $($(this).parent().find('input')).val('');
                $($(this).parent().find('input')).attr('disabled',true);
             } else {
                $($(this).parent().find('input')).removeAttr('disabled',false);
             }
        });

        $(document).on('click', '#variance_toggle', function(e){
            e.preventDefault();
            OptionFile.toggle_variance(session.option_files);
        });

    //BMD options - BMR

        $("#bmr_setup_tbl").on('click', '.bmr_edit', function(e){
            e.preventDefault();
            var tr =  $(this).parent().parent()[0];
            if (crud == 'Read'){
                $(this).parent().parent().data('bmr').build_settings_tbl(tr);
            } else {
                $(this).parent().parent().data('bmr').build_settings_form(tr);
            }

            $('#bmr_settings_form').modal({
                    backdrop: true,
                    keyboard: true
                });
        });

        $('#bmr_new').click(function(e){
            e.preventDefault();
            var new_bmr = $('#bmr_select option:selected').data('bmr').clone();
            new_bmr.build_settings_form('new');
            $('#bmr_settings_form').modal({
                    backdrop: true,
                    keyboard: true
                });
        });

        $("#bmr_settings_save").click(function(){
            if ($('#bmr_settings_form').data('bmr').save_from_form()) {
                $('#bmr_settings_form').modal('toggle');
            }
        });

        $("#bmr_settings_close").click(function(){
            $('#bmr_settings_form').modal('toggle');
        });

        $("#bmr_settings_delete").click(function(){
            $('#bmr_settings_form').data('bmr').remove();
        });

        //BMD execution
        $('#BMDS_run').click(function(e){
            e.preventDefault();
            // set run status
            $('#BMDS_runstatus').remove();
            var status = $('<div id="BMDS_runstatus"></div>')
                            .append('<p>Running BMDS please wait... <img id="BMDS_runstatus" src="/static/img/loading.gif" /></p>');
            $('#BMDS').append(status);
            var d = session.submit_settings();
            var args = JSON.stringify(d);
            $.post(url_run_model, args, function(d) {
                $('#selection_div').remove();
                $('#BMDS_runstatus').remove();
                crud = "Edit";
                results = $.parseJSON(d);
                session = new Session(results, endpoint, logics, crud, bmds_version);
                $('#bmd_logic_tab').trigger('click');
            });
        });

        $('#BMDS_reset').click(function(e){
            e.preventDefault();
            $('#BMDS_runstatus').remove();
            $.get(url_template, "", function(d) {
                crud = "Create";
                session = new Session(d, endpoint, logics, crud, bmds_version);
            });
        });

    //BMD Output

        // load output modal
        $("#bmd_output_tbl tbody").on("click", ".bmd_outfile", function(e){
            e.preventDefault();
            e.stopPropagation();
            var bmd = $(this).parent().parent().data('d');
            bmd.show_modal(raw_output_img);
        });

        // add new hover BMD model
        $("#bmd_output_tbl > tbody").on("mouseover", "tr", function(){
            var d = $(this).data('d');
            if ((d.hasOwnProperty('plotting')) && (typeof(d.plotting)=="object")){
                bmd_output_plot.add_bmd_line(d, 'd3_bmd_hover');
            }
        });

        $("#bmd_output_tbl > tbody").on("mouseout", "tr", function(){
            var d = $(this).data('d');
            bmd_output_plot.clear_bmd_lines('d3_bmd_hover');
        });

        // add new hover BMD model
        $("#bmd_output_tbl > tbody").on("mouseover", "td", function(e){
            var d = $(this).data('d');
            if ((d) && (d.hasOwnProperty('plotting')) && (typeof(d.plotting)=="object")){
                bmd_output_plot.add_bmd_line(d, 'd3_bmd_hover');
                e.stopPropagation();
            }
        });

        $("#bmd_output_tbl > tbody").on("mouseout", "td", function(e){
            var d = $(this).data('d');
            if (d){
                bmd_output_plot.clear_bmd_lines('d3_bmd_hover');
                e.stopPropagation();
            }
        });

    //Load BMD Setup Tab
    bmd_ds_plot.build_plot();
    session.endpoint.build_endpoint_table($('#bmd_dr_tbl'));
    $('#bmd_dr_tbl').data('d', session.endpoint);
    if (crud !== 'Read'){get_model_options();}
});

var get_model_options = function(){
    //after complete, load possible model options
    args = {};
    $.getJSON(url_options, args , function(data) {
        var sel = $('#bmds_options_select');
        sel.contents().remove();
        data.options.forEach(function(v){
            sel.append('<option>' + v + '</option>)');
        });
        sel = $('#bmr_select');
        sel.contents().remove();

        data.bmrs.forEach(function(v){
            var d = new BMR(session, v);
            var opt = $('<option>' + v.type + '</option>)').data('bmr', d);
            sel.append(opt);
        });
    });
};

var load_option_file = function(model, sel){
    //Load the default selected option file into the document
    var type = $('#bmd_dr_tbl').data('d').data.data_type;
    var args = {};
    var url = '/bmd/' + bmds_version +'/model_option/' + type + '/'+model+'/';
    $.getJSON(url, args , function(data) {session.add_option(data);});
};
