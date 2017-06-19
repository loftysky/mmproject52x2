jQuery(function(J) {

    var M = mm52x2;

    var devModeToggle = $('#dev-mode-toggle')
    var devControls = $('#dev-controls')

    if (M.devMode) {
        devModeToggle.attr('checked', true)
        devControls.removeClass('hide')
    }
    
    devModeToggle.on('click', function() {
        devMode = devModeToggle.is(':checked');
        M.setDevMode(devMode);

        // We only show the dev controls. We don't hide them again.
        if (devMode) {
            devControls.removeClass('hide')
        }
    })

    J('#dev-ping').on('click', function() {
        M.send({type: 'ping'})
    })
    M.handlers.pong = function(msg) {
        alert('Pong (from Python)!')
    }

    J('#dev-raise-error').on('click', function() {
        M.send({type: 'debug_raise_error'})
    })

    J('#dev-reload').on('click', function() {
        location.reload()
    })

    // J('#dev-console-toggle').on('click', function() {
    //     $('#dev-console').toggleClass('hide')
    // })


})