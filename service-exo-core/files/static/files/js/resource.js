var ResourceRelated = function(slug){
    this.slug = slug;
    this.initViews();
    this.channelName = 'resources';
    this.resourceChannel = Backbone.Radio.channel(this.channelName);
    this.resourceChannel.on('add-resource', _.bind(this.onResourceAdd, this));
};

ResourceRelated.prototype.initViews = function(){
    this.ResourceCollectionView = Backbone.View.extend({
        el: '#dev__resources',
        events: {
            'click .dev__remove': 'removeResource'
        },
        initialize: function(options){
            this.resources = options.resources;
            this.slug = options.slug;
            this.channelName = options.channelName  || 'resources';
            this.resourceChannel = Backbone.Radio.channel(this.channelName);
            this.listenTo(this.resources, 'add', this.addResource);
            this.listenTo(this.resources, 'remove', this.removeEventResource);
            this.resources.fetch({ data: $.param({ "tags__name": this.slug}) });
        },
        addResource: function(model){
            model.set('slug', this.slug);
            var html = templates.resources_list_item(model.toJSON());
            this.$el.find('#dev__resource_container').append(html);
        },
        removeResource: function(event){
            event.preventDefault();
            var slug = $(event.currentTarget).data('slug');
            var elem_id = $(event.currentTarget).data('pk');
            var resource = new window.Model.Resource({id: elem_id});
            resource.removeTag(this.slug, _.bind(this.onTagRemoved, this));
        },
        onTagRemoved: function(response){
            var resource = new window.Model.Resource(response);
            this.resources.remove(resource);
            toastr_manager.show_message("success", 'Resource removed successfully');
        },
        removeEventResource: function(model){
            this.$el.find('.dev__resource__' + model.id).remove();
        }
    });
    $('#dev__add_resource').click(_.bind(this.showAddResource, this));
};

ResourceRelated.prototype.showResources = function(){
    this.resources = new window.Collection.ResourceCollection();
    this.resource_view = new this.ResourceCollectionView({
        resources: this.resources,
        slug: this.slug
    });
};

ResourceRelated.prototype.showAddResource = function(event){
    var assignment = $(event.currentTarget).data('slug');
    var project = $(event.currentTarget).data('project');
    var view = new window.View.ResourceModal({
        assignment: assignment,
        project: project,
    });
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: "Add resources",
        animate: true,
        okText: 'Save'
    });
    modal.open();
};

ResourceRelated.prototype.onResourceAdd = function(resource){
    this.resources.add(resource);
    toastr_manager.show_message("success", 'Resource added successfully');
};

$(function(){
    var slug = $('#dev__resources').data('slug');
    var view = new ResourceRelated(slug);
    view.showResources();
});
