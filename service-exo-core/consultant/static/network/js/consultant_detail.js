$(document).ready(function(){

    var channel = Backbone.Radio.channel('master-detail');
    var view_trained, view_badge;
    channel.on('detail-opened', function(){
        if (view_badge){
            view_badge.close();
            view_trained.close();
            $('.dev__resend_invitation_btn').unbind('click');
        }
        if($('#dev__trained').length > 0){
            view_trained = new window.View.TrainedConsultant();
        }

        $('.dev__resend_invitation_btn').click(function(event){
            var l = $(this).ladda();
            l.ladda('start');
            event.preventDefault();
            var invitation_id = $(event.currentTarget).data('pk');
            $.ajax({
                type: 'put',
                url: urlservice.resolve('resend-invitation', invitation_id),
                success: function(){
                    l.ladda('stop');
                    l.removeClass('ladda-button');
                    toastr_manager.show_message('success',
                                                '',
                                                'Invitation re-sent successfully');
                }
            });
        });
        $('.dev__confirm_badge_btn').click(function(event){
            var l = $(this).ladda();
            l.ladda('start');
            event.preventDefault();
            var url = $(event.currentTarget).data('href');
            $.ajax({
                type: 'put',
                url: url,
                success: function(){
                    l.ladda('stop');
                    l.removeClass('ladda-button');
                    toastr_manager.show_message('success',
                                                '',
                                                'Badge confirmed successfully');
                }
            });
        });
        $('.dev__public-site').iCheck(icheck_options.get_defaults());
        $('#dev__is_exo_certified').iCheck(icheck_options.get_defaults());
        $('.dev__public-site').on('ifChanged', mark_element);
        $('#dev__is_exo_certified').on('ifChanged', mark_exo_certified);
    });

    function mark_element(event){
        var consultant_id = $(event.currentTarget).data('consultant');
        var public_site_type = $(event.currentTarget).data('site_type');
        $.ajax({
            url: urlservice.resolve('consultant-toggle-web-status',
                                    consultant_id,
                                    public_site_type),
            type: 'put',
            success: function(){
                toastr_manager.show_message(
                    'success',
                    '',
                    'Status changed');
            }
        });
    }

    function mark_exo_certified(event){
        var consultant_id = $(event.currentTarget).data('consultant');
        var data = {status: $(event.currentTarget).is(':checked')};
        $.ajax({
            url: urlservice.resolve('consultant-toggle-exo-certified', consultant_id),
            type: 'put',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(){
                toastr_manager.show_message(
                    'success',
                    '',
                    'Status Certified changed');
            }
        });
    }
});
