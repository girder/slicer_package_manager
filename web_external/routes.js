import _ from 'underscore';

import {getCurrentUser, setCurrentUser} from 'girder/auth';
import events from 'girder/events';

import router from './router';

function navigateTo(View, settings) {
    events.trigger('g:navigateTo', View, settings, null);
}

// TODO
