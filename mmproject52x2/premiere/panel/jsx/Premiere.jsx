if (typeof($) == 'undefined') $ = {};
$._MYFUNCTIONS = {

    test: function(x) {
        $.writeln("were in jsx");
        $.writeln(x)
        return "JSX before\nafter"
    }

}