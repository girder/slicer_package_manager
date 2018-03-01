import events from 'girder/events';
import router from 'girder/router';
import {exposePluginConfig} from 'girder/utilities/PluginUtils';

import ConfigView from './views/ConfigView';

exposePluginConfig('slicer_package_manager', 'plugins/slicer_package_manager/config');

router.route('plugins/slicer_package_manager/config', 'slicerConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
