jQuery(function(J) {

    var M = mm52x2;

    var devModeToggle = $('#dev-mode-toggle')
    var devControls = $('#dev-controls')

    if (M.devMode) {
        devModeToggle.attr('checked', true)
    }
    
    devModeToggle.on('click', function() {
        devMode = devModeToggle.is(':checked');
        M.setDevMode(devMode);
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

    J('#dev-environ').on('click', function() {
        M.send({type: 'call', func: 'mmproject52x2.premiere.runtime:debug_environ'}, function(res) {
            alert(res)
        })
    })


    J('#dev-reload').on('click', function() {
        location.reload()
    })


})