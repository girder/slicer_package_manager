import Backbone from 'backbone';
import $ from 'jquery';
import _ from 'underscore';

import GirderApp from 'girder/views/App';

__webpack_public_path__ = '/static/built/plugins/slicer_extension_manager/'; // eslint-disable-line no-undef, camelcase

const SlicerApp = GirderApp.extend({
    start: function () {
        return GirderApp.prototype.start.apply(this, arguments);
    },

    bindGirderEvents: function () {
        // This might be overridden in the near future
        GirderApp.prototype.bindGirderEvents.apply(this, arguments);
    },

    _createLayout: function () {
        // Prevent the default behavior
    },

    render: function () {
        if (!this._started) {
            return;
        }

        return this;
    },

    navigateTo: function () {},

    login: function () {
        // Re-implement this, to use ISIC's instance of the router
        // TODO: if the router were stored as an App instance property, this wouldn't be necessary
        let route = splitRoute(Backbone.history.fragment).base;
        Backbone.history.fragment = null;
        eventStream.close();

        if (getCurrentUser()) {
            eventStream.open();
            router.navigate(route, {trigger: true});
        } else {
            router.navigate('/', {trigger: true});
        }
    }
});

export default SlicerApp;
