import $ from 'jquery';

import events from 'girder/events';

import SlicerApp from './app.js';

$(() => {
    events.trigger('g:appload.before');
    const app = new SlicerApp({
        el: 'body',
        parentView: null
    });
    events.trigger('g:appload.after', app);
});