
'''

- logs in /Volumes/CGroot/home/mikeb/Library/Logs/CSXS

- javascript logs (via console.log) into CEPHtmlEngine6-PPRO-11.0.0-com.mminternals.mm52x2.main.log

    [0615/135647:INFO:CONSOLE(12)] ""HERE before\nafter"", source: file:///Volumes/CGroot/home/mikeb/Library/Application%20Support/Adobe/CEP/extensions/mm52x2_panel/index.html (12)
    [0615/135647:INFO:CONSOLE(18)] ""back from test:" "JSX before\nafter"", source: file:///Volumes/CGroot/home/mikeb/Library/Application%20Support/Adobe/CEP/extensions/mm52x2_panel/index.html (18)
    [0615/140002:INFO:CONSOLE(12)] ""before\"after"", source: file:///Volumes/CGroot/home/mikeb/Library/Application%20Support/Adobe/CEP/extensions/mm52x2_panel/index.html (12)

    it only has strings. objects are tossed out.

- JSX logs (via $.writeln) into CEP6-PPRO.log
    
    all of these are before\nafter

    2017-06-15 13:56:47:464 : DEBUG PlugPlugEvalScriptFn() callback called. EngineId: com.mminternals.mm52x2.main_Engine_Id, Script: $._MYFUNCTIONS.test('before\nafter')
    2017-06-15 13:56:47:468 : DEBUG PlugPlugEvalScriptFn() callback returned: PlugPlugErrorCode_success
    2017-06-15 13:56:47:470 : DEBUG outResult value of PlugPlugEvalScript() : JSX before
    after