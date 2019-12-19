import sys

TEST_MODE = sys.argv[1:2] == ['test']

if TEST_MODE:
    TEST_INSTALLED_APPS = ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware']
else:
    MIDDLEWARE = []
    TEST_INSTALLED_APPS = []
