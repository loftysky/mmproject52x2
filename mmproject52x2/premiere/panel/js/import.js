
(function(M) {

M.import = function(glob, bin_name) {

    M.send({'type': 'call', 'func': 'mmproject52x2.render.locate:by_glob', 'args': [glob]}, function(res) {

        var total = 0
        var exists = 0
        var images = []
        jQuery.each(res, function(shot, path) {
            ++total
            if (path) {
                ++exists
                images.push(path)
            }
        })

        alert("Found " + total + " shots; " + (total - exists) + " were missing frames.")

        var encoded_images = JSON.stringify(images)
        var encoded_bin_name = JSON.stringify(bin_name)
        var source = "$._mm52x2.importImages(" + encoded_images + ", " + encoded_bin_name + ")"
        M.log('evalScript: ', source)
        window.__adobe_cep__.evalScript(source, function(res) {
            M.log("We are back!")
        })

    })

}


})(mm52x2)
