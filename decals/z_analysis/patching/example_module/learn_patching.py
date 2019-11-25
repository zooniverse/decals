from patching.example_module.learn_patching_external import some_external_function


def some_function():
    return 'original function called'


def call_external_function():
    return some_external_function()