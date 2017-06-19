
if ($ === undefined) {
    $ = {}
}

$._mm52x2 = (function() {

    var M = {}

    var TYPE_ROOT = 3
    var TYPE_BIN = 2
    var TYPE_CLIP = 1 // Clip or sequence.

    var getItem = function(name, node) {
        var parts = name.split(/[\/\\]/)
        node = node || app.project.rootItem
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i]
            if (!part.length) {
                continue
            }
            var children = node.children
            var numItems = children.numItems
            var found = false
            for (var j = 0; j < numItems; j++) {
                var child = children[j]
                if (child.name == part) {
                    found = true
                    node = child
                    break
                }
            }
            if (!found) {
                return
            }
        }
    }

    var walk = function(func, item, depth) {
        item = item || app.project.rootItem
        depth = depth || 0
        func(item, depth)
        var children = item.children
        var numItems = children ? children.numItems : 0
        for (var i = 0; i < numItems; i++) {
            var child = children[i]
            if (child) {
                walk(func, child, depth + 1)
            }
        }
    }

    M.importImages = function(images, binName) {

        var bin = app.project.rootItem.createBin(binName);

        for (var i = 0; i < images.length; i++) {
            // We still need to do them one at a time.
            app.project.importFiles(
                [images[i]],
                0, // Don't silence errors.
                bin,
                1, // As image sequences.
            ); 
        }

    }

    M.getAllFootage = function() {

        var res = {}

        walk(function(node, depth) {
            
            if (node.type != TYPE_CLIP) {
                return
            }
            if (!node.canChangeMediaPath()) {
                return
            }

            var nodePath = node.treePath.replace(/\\/g, '/')
            var xml = node.getProjectMetadata();
            var m = /<premierePrivateProjectMetaData:Column\.Intrinsic\.FilePath>(.*?)<\//.exec(xml)
            if (m) {
                var filePath = m[1]
                res[nodePath] = filePath
            }
        })

        return res

    }

    M.replaceFootage = function(replacements) {

        var count = 0

        walk(function(node) {

            var nodePath = node.treePath.replace(/\\/g, '/')
            var filePath = replacements[nodePath]
            $.writeln(nodePath + ' ' + filePath)
            if (filePath && node.canChangeMediaPath()) {
                count++
                node.changeMediaPath(filePath)
            }

        })

        return count

    }

    return M

})()
