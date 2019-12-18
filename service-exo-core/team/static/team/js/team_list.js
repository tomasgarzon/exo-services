$(function(){

    function show_modal_email(teams){
        var view = new window.View.SendEmail({
                project_id: $('table.list-detail').data('project'),
                teams: teams
            });
            var modal = new Backbone.BootstrapModal({
                content: view,
                title: "Email the teams",
                animate: true,
                okText: 'Send'
            });
            modal.open();
    }

    $('#bulkaction-form').submit(function(event){
        var elem = $(this);
        if (elem.find('#id_actions').val() == 'email_teams' ){
            event.preventDefault();
            var object_list = [];
            $.each($('table.list-detail input[type=checkbox]:checked'), function(index, object){
                object_list.push($(object).prop('id'));
            });
            show_modal_email(object_list);
        }
    });
    $('body').on('click', '.dev__send_email', function(event){
        event.preventDefault();
        var elem = $(event.currentTarget);
        var teams = [elem.data('team')];
        show_modal_email(teams);
    });
});
