/**
 * This file is part of Invenio-JSONSchemas.
 * Copyright (C) 2015 CERN.
 *
 * Invenio-JSONSchemas is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio-JSONSchemas is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio-JSONSchemas; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
 * MA 02111-1307, USA.
 *
 * In applying this license, CERN does not
 * waive the privileges and immunities granted to it by virtue of its status
 * as an Intergovernmental Organization or submit itself to any jurisdiction.
 */

// use a renderjson placeholder, because AMD does not seem to work here
require(['jquery', 'vendors/renderjson/renderjson'], function($, _renderjson) {
  'use strict';

  $(function() {
    function linkify(target) {
        $('.key', target).each(function() {
            var element = this;

            // test if the key is "$ref"
            var text = $(element).text();
            if (text === '"$schema"' || text === '"$ref"') {
                // now search the first '.string' element after
                // the key element, on the same tree level
                // (i.e. a sibling)
                var parent = $(element).parent();
                var siblings = $(parent).children();
                var seen = false;
                for (var i = 0; i < siblings.length; ++i) {
                    var sibling = siblings[i];
                    if (seen) {
                        if ($(sibling).hasClass('string')) {
                            // store text and empty node
                            var txt = $(sibling).text();
                            $(sibling).empty();

                            // strip quotes
                            var url = txt.substring(1, txt.length - 1);

                            // create link element
                            var a = $('<a>');
                            a.attr('href', '#' + url);
                            a.text(txt);

                            // add link to element
                            $(sibling).append(a);

                            // done
                            break;
                        }
                    } else {
                        if (sibling === element) {
                            seen = true;
                        }
                    }
                }
            }
        });
    }

    function whitelistedUrl(url) {
        return url.startsWith(location.origin)
            || url.startsWith('http://json-schema.org/')
            || url.startsWith('https://json-schema.org/');
    }

    function update() {
        if (location.hash.startsWith('#') && location.hash.length > 1) {
            var url = location.hash.substring(1);

            // security check
            if (whitelistedUrl(url)) {
                // strip fragment from url
                var file = url.split('#')[0];
                $.getJSON(file, function(data) {
                    var target = $('#jsonschema-detailed');

                    // set new detailed view
                    target.empty();

                    var rawlink_file = file;
                    if (rawlink_file.startsWith(location.origin)) {
                        rawlink_file = rawlink_file.replace(location.origin + '/jsonschemas/', '');
                    }

                    var rawlink = $('<a>');
                    rawlink.attr('href', url);
                    rawlink.text('Schema: ' + rawlink_file);
                    rawlink.addClass('rawlink');
                    target.append(rawlink);

                    renderjson.set_show_to_level(4);
                    target.append(renderjson(data));

                    // link all refs
                    linkify(target);

                    // mark active link
                    $('.jsonschema-link').removeClass('active');
                    $(document.getElementById('link-' + url)).addClass('active');
                });
            }
        }
    }

    $(window).bind('hashchange', update);
    update();
  });
});
