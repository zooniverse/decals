from patching.example_module import learn_patching

"""
See:
https://krzysztofzuraw.com/blog/2016/mocks-monkeypatching-in-python.html
https://docs.pytest.org/en/latest/monkeypatch.html
"""


def test_some_function(monkeypatch):
    # define the function to use instead
    def mock_function():
        return 'new function called'
    # tell pytest to use this function
    # class (here, a whole script), attribute (here, a method), new value (here, a different method)
    monkeypatch.setattr(learn_patching, 'some_function', mock_function)
    x = learn_patching.some_function()
    assert x == 'new function called'


def test_some_function_with_external_dependence(monkeypatch):
    # define the function to use instead
    def mock_external_function():
        return 'new external function called'
    # monkeypatch.setattr('learn_patching_external.some_external_function', mock_external_function)  # wrong
    # monkeypatch.setattr('example_module.learn_patching.some_external_function', mock_external_function)  # wrong, init.py breaks
    monkeypatch.setattr(learn_patching, 'some_external_function', mock_external_function)  # right - import elsewhere
    x = learn_patching.call_external_function()
    assert x == 'new external function called'  # doesn't work when the class is imported locally to real module?
