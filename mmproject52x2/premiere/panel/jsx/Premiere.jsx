if (typeof($) == 'undefined') $ = {};

$.writeln('HERE WE ARE 1')

$._mm52x2 = {

    importImages: function(images, bin_name) {

        $.writeln("HERE WE ARE 2");
        // return;

        var bin = app.project.rootItem.createBin(bin_name);

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

}
