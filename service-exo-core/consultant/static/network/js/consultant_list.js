var NetworkListView = function(){
    this.channelName = 'network';
    this.channel = Backbone.Radio.channel(this.channelName);
    this.init_events();
    this.init_settings();
};

NetworkListView.prototype.init_events = function(){
    $('#dev__export-csv, #dev__export-pdf').click(function(event){
        event.preventDefault();
        var data = $('#dev__search-network-list').serialize();
        var href = $(event.currentTarget).data('href') + "?" + data;
        location.href = href;
    });
    $('#dev__export-bio').click(_.bind(this.showModalExportBioPackage, this));

};

NetworkListView.prototype.init_settings = function(){
    $('#dev__toggle_settings').click(_.bind(this.showModalSettings, this));
};


NetworkListView.prototype.showModalSettings = function(){
    var collection = new window.Collection.UserSectionPreference();
    collection.section = settings.user_preference.SECTION_CH_NETWORK;
    collection.fetch({async: false});
    var model = collection.models[0];
    var view = new window.View.UserSectionPreference({
        model: model,
        channelName: this.channelName
    });
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: "Select fields",
        animate: true,
        okText: 'Save'
    });
    modal.open();

    this.channel.on('save-fields', _.bind(this.processModalSettings, this));
};

NetworkListView.prototype.processModalSettings = function(selected, model){
    model.set('table', selected);
    model.save([], {success: _.bind(this.processSuccessSettings, this)});
};

NetworkListView.prototype.processSuccessSettings = function(){
    toastr_manager.show_message(
        'success',
        "Fields stored successfully",
        ''
    );
    location.href = ".";
};

NetworkListView.prototype.processTrack = function(){
    if (analytics.woopra){
        woopra.track('network-filter_2', {
            search: window.location.search
        });
    }
};


NetworkListView.prototype.showModalExportBioPackage = function(event){
    var model = new window.Model.SectionFields();
    model.section = settings.user_preference.SECTION_CH_NETWORK;
    model.fetch({async: false});
    var view = new window.View.ExportBioPackage({
        url: $(event.currentTarget).data('href'),
        model: model
    });
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: "Select consultants",
        animate: true,
        okText: 'Generate bios'
    });
    modal.open();
};

$(function(){
    var view = new NetworkListView();
    view.processTrack();
});
