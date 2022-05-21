/* ========================================================================
 * Tour Event
 * ======================================================================== */
'use strict';

var template = '<div class="popover" role="tooltip"> <div class="arrow"></div>' +
    ' <h3 class="popover-title"></h3> <div class="popover-content">' +
    '</div> <div class="popover-navigation"> <div class="btn-group"> ' +
    '<button class="btn btn-sm btn-default" data-role="prev" style="padding: 5px 10px;"> Anterior </button> ' +
    '<button class="btn btn-sm btn-default" data-role="next" ' +
    'style="padding: 5px 10px;">Proximo </button> ' +
    '<button class="btn btn-sm btn-default" data-role="pause-resume" data-pause-text="Pause" ' +
    'data-resume-text="Resume" style="padding: 5px 10px;">Pausa</button> </div> ' +
    '<button class="btn btn-sm btn-default" data-role="end" style="padding: 5px 10px;' +
    ' margin-left: 10px;">Finalizar</button> </div> </div>';
var tour;
var typingOut;
function xinguTour(name, array) {
    tour = new Tour({
        name: makeName(name),
        debug: true,
        template: template,
        steps: array
    });
    tour.init();
}

function makeName(name) {
    return name.replace(/\//g, '_').replace(/:/g, '_')
        .replace(/\./g, '__dot__').replace(/\-/g, '__dash__')
        .replace(/[?]/g, '_int_').replace(/[%]/g, '_per_')
        .replace(/[=]/g, '').replace(/[&]/g, '');
}


// Esta funcao limpa a tour da tela desejada.
function clearTour(name) {
    localStorage.removeItem(name + '_current_step');
    localStorage.removeItem(name + '_end');
    if (tour != undefined) {
        tour.restart();
    }
}

function typing(string, element, bool, milliseconds) {
    if (bool) {
        var ZERO = 0;
        (function writer(i) {
            if (string.length <= i++) {
                element.value = string;
                $('#' + element.id).change();
                return;
            }
            element.value = string.substring(ZERO, i);
            if (element.value[element.value.length - 1] != ' ') {
                element.focus();
            }
            typingOut = setTimeout(function () {
                writer(i);
            }, milliseconds);
        })(ZERO);
    } else {
        clearTimeout(typingOut);
        $('.form-control').val('');
        $('.form-control').change();
    }
}
