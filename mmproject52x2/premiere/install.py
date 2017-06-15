import argparse
import errno
import os
import subprocess


def main():

    print 'Making extension root directory.'
    ext_root = os.path.expanduser('~/Library/Application Support/Adobe/CEP/extensions')
    try:
        os.makedirs(ext_root)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    link_path = os.path.join(ext_root, 'mm52x2_panel')
    real_path = os.path.abspath(os.path.join(__file__, '..', 'panel'))
    try:
        os.unlink(link_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.symlink(real_path, link_path)

    print 'Asserting debug mode.'
    # Note that Premiere 2017 is currently sitting at CSXS 6.
    subprocess.check_call(['defaults', 'write', 'com.adobe.CSXS.6', 'PlayerDebugMode', '1'])
    
    # Need to force macOS to recache.
    subprocess.check_call(['killall', '-u', os.getlogin(), 'cfprefsd'])
    
    # log level: defaults write com.adobe.CSXS.6 LogLevel 4
    # See: https://github.com/Adobe-CEP/CEP-Resources/wiki/CEP-6-HTML-Extension-Cookbook-for-CC-2015#where-are-the-log-files
    # Logs go to ~/Library/Logs/CSXS

    print 'Done.'