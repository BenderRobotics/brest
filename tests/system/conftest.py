def pytest_addoption(parser):
    parser.addoption("--needed", action="store", default=None, help="Comma-separated list of needed resources for system tests")