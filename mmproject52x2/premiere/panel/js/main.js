
var log = function() {

    var args = Array.prototype.slice.call(arguments)
    var msg = "[mm52x2] " + args.join(" ")
    console.log(msg)
    
}

var mm52x2 = (function() {

    log('Starting main.js')

    var M = {}
    M.log = log

    // Hooray for Node!
    var spawn = require('child_process').spawn

    M.devMode = window.localStorage.mm52x2_devMode == '1'
    M.setDevMode = function(x) {
        M.devMode = !!x
        log("devMode:", M.devMode ? "ON": "OFF")
        window.localStorage.mm52x2_devMode = M.devMode ? '1' : '0'
    }

    var proc = null

    var assertProc = function() {

        if (proc !== null) {
            return proc
        }

        if (M.devMode) {
            log("Starting runtime in devMode.")
            proc = spawn('/bin/bash', [
                '-lc', 'dev python -m mmproject52x2.premiere.runtime'
            ])
        } else {
            log("Starting runtime.")
            proc = spawn('/bin/bash', [
                '-lc', 'python -m mmproject52x2.premiere.runtime'
            ])
        }
        
        proc.stdout.on('data', onProcData)
        proc.on('close', onProcClose)

        return proc

    }

    var onProcData = function(data) {
        
        var out = data.toString()
        var lines = out.split(/(\r?\n)+/g)

        for (var i = 0; i < lines.length; i++) {
            var encoded = lines[i]
            encoded = encoded.replace(/^\s+|\s+$/g, '')
            if (!encoded.length) {
                continue
            }
            log("Recv:", encoded)

            try {
                var msg = JSON.parse(encoded)
            } catch(e) {
                log("Error during JSON.parse:", e)
                continue
            }

            try {
                handleMessage(msg)
            } catch (e) {
                log("Error during handleMessage:", e)
            }
        }

    }


    var onProcClose = function(code) {
        log("Runtime died:", code)
        proc = null;
    }

    M.handlers = {};

    M.handlers.hello = function(msg) {
        msg.type = 'elloh'
        M.send(msg)
    }
    M.handlers.elloh = function(msg) {}

    M.handlers.ping = function(msg) {
        msg.type = 'pong'
        M.send(msg)
    }
    M.handlers.pong = function(msg) {}

    M.handlers.error = function(msg) {
        alert((msg.error_type || 'Exception') + ' from Python: ' + (msg.error || '<< No message. >>'))
    }



    var handleMessage = function (msg) {

        var type = msg.type
        if (!type) {
            log("Message has no type.")
            return
        }

        var func = M.handlers[type]
        if (!func) {
            log("No handler for type:", type)
            return
        }

        func(msg)
                
    }


    var send_count = 0
    var resultCallbacks = {}

    M.send = function(msg, callback) {


        msg.id = ++send_count
        if (callback) {
            resultCallbacks[msg.id] = {
                startTime: new Date(),
                callback: callback
            }
        }

        var encoded = JSON.stringify(msg)

        assertProc().stdin.write(encoded + '\n')
        log("Send:", encoded)

    }

    M.handlers.result = function(msg) {

        var id = msg.id
        if (!id) {
            return
        }

        var data = resultCallbacks[id]
        resultCallbacks[id] = null

        if (!data) {
            return
        }

        data.callback(msg.result)

    }


    M.callJSX = function(funcName, args, callback) {
        var encodedArgs = []
        args = args || []
        for (var i = 0; i < args.length; i++) {
            encodedArgs.push(JSON.stringify(args[i]))
        }
        var source = funcName + '(' + encodedArgs.join(', ') + ')'
        source = 'JSON.stringify(' + source + ')'
        M.log('evalScript: ' + source)
        window.__adobe_cep__.evalScript(source, function(res) {
            try {
                res = res ? JSON.parse(res) : null;
            } catch (e) {
                M.log('WARNING: Response was not JSON.')
            }
            if (callback) {
                callback(res)
            }
        })
    }

    M.callOurJSX = function(funcName, args, callback) {
        M.callJSX('$._mm52x2.' + funcName, args, callback)
    }

    return M;

})();

