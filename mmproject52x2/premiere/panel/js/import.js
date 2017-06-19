
(function(M) {

M.import = function(glob, binName) {

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

        var ok = confirm("Found " + total + " shots; " + (total - exists) + " were missing frames.\n\nImport these shots?")
        if (!ok) {
            return
        }
        
        M.callOurJSX('importImages', [images, binName], function(res) {
            M.log("We are back!")
            alert("Make sure to change their frame rate to 24!")
        })

    })

}


jQuery(function(J) {

    var importButton = J('#import-button')
        .attr('disabled', false)
        .on('click', function(e) {
            e.preventDefault()
            M.import(
                J('#import-glob').val(),
                J('#import-bin').val()
            );
        })

})


})(mm52x2)
