import {restRequest} from 'girder/rest';
import events from 'girder/events';
import View from 'girder/views/View';

import ConfigViewTemplate from '../templates/configView.pug';

// import PluginConfigBreadcrumbWidget from 'girder/views/widgets/PluginConfigBreadcrumbWidget';

const ConfigView = View.extend({
    events: {},

    initialize: function () {
        restRequest({
            method: 'GET',
            url: 'app/5a223e74c9c5cb2925f7972a/release/5a223ea3c9c5cb2925f7972b/extension',
            data: {}
        })
            .done((resp) => {
                console.log(resp);
                this.extensions = resp;
                this.render();
            });
    },

    render: function () {
        this.$el.html(ConfigViewTemplate({
            extensions: this.extensions
        }));
        return this;
    },

    _saveSettings: function (settings) {
        restRequest({
            type: 'PUT',
            path: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        })
            .done(() => {
                events.trigger('g:alert', {
                    icon: 'ok',
                    text: 'Settings saved.',
                    type: 'success',
                    timeout: 4000
                });
            })
            .fail((resp) => {
                this.$('#slicer-config-error-message').text(resp.responseJSON.message);
            });
    }
});

export default ConfigView;
