
var log = function() {
    var args = Array.prototype.slice.call(arguments)
    var msg = "[mm52x2] " + args.join(" ")
    console.log(msg)
}

var mm52x2 = (function() {

log('Starting main.js')

var M = {}

M.devMode = window.localStorage.mm52x2_devMode == '1'
M.setDevMode = function(x) {
    M.devMode = !!x
    log("devMode:", M.devMode ? "ON": "OFF")
    window.localStorage.mm52x2_devMode = M.devMode ? '1' : '0'
}


var pid = null
var proc = window.cep.process

var assertProc = function() {

    if (pid && proc.isRunning(pid).data) {
        return
    }

    if (M.devMode) {
        log("Starting runtime in devMode.")
        pid = proc.createProcess(
            '/usr/local/vee/src/bin/vee', 'exec', '--dev',
            'python', '-m', 'mmproject52x2.premiere.runtime'
        ).data
    } else {
        log("Starting runtime.")
        pid = proc.createProcess(
            '/usr/local/vee/src/bin/vee', 'exec',
            'python', '-m', 'mmproject52x2.premiere.runtime'
        ).data
    }
    
    pollStdout()

}


var onQuit = function(reason) {
    log("Runtime died:", reason)
    pid = null;
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


var pollStdout = function() {
    
    if (!pid) {
        return;
    }
    
    proc.stdout(pid, function(out) {
        var lines = out.split(/(\r?\n)+/)
        for (var i = 0; i < lines.length; i++) {
            var encoded = lines[i]
            encoded = encoded.replace(/^\s+|\s+$/g, '')
            if (!encoded.length) {
                continue
            }
            log("Recv:", encoded)

            var msg = JSON.parse(encoded)
            try {
                handleMessage(msg)
            } catch (e) {
                log("Error during handleMessage:", e)
            }

        }
    })

    if (proc.isRunning(pid).data) {
        // We do need to keep calling this, unfortunately.
        setTimeout(pollStdout, 30);
    }

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

    assertProc();

    msg.id = ++send_count
    if (callback) {
        resultCallbacks[msg.id] = {
            startTime: new Date(),
            callback: callback
        }
    }

    var encoded = JSON.stringify(msg)
    log("Send:", encoded)

    proc.stdin(pid, encoded + '\n')

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









M.import = function() {

    // M.send({'type': 'ping', 'key': 123})

}




return M;

})();

