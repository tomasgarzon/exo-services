# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',  # activate coverage report
    '--with-doctest',  # activate doctest: find and run docstests
    '--verbosity=0',   # verbose output
    '--with-xunit',    # enable XUnit plugin
    '--xunit-file=xunittest.xml',  # the XUnit report file
    '--cover-xml',     # produle XML coverage info
    '--cover-xml-file=coverage.xml',  # the coverage info file
    # You may also specify the packages to be covered here
    # '--cover-package=blog,examples'
]
