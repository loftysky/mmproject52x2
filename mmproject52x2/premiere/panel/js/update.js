
(function(M) {

M.update = function() {
    M.callOurJSX('getAllFootage', [], function(res) {
        M.send({'type': 'call', 'func': 'mmproject52x2.render.locate:newer', 'args': [res]}, M._updateStage2)
    })
}

M._updateStage2 = function(res) {

    var counts = {unknown: 0, newer: 0, nochange: 0}
    var replacements = {}
    for (var i = 0; i < res.length; i++) {
        var data = res[i]
        var type = data.type
        type = counts[type] === undefined ? 'unknown' : type
        counts[type]++
        if (type == 'newer') {
            replacements[data.name] = data.path
        }
    }
    var ok = confirm('Found: '
        + counts.newer + ' newer, '
        + counts.nochange + ' unchanged, and '
        + counts.unknown + ' unknown.\n\nReplace footage?'
    )
    if (!ok) {
        return
    }

    if (counts.newer) {
        M.callOurJSX('replaceFootage', [replacements], function(res) {})
    }

}



jQuery(function(J) {

    J('#update-button')
        .attr('disabled', false)
        .on('click', function(e) {
            e.preventDefault()
            M.update()
        })

})


})(mm52x2)

