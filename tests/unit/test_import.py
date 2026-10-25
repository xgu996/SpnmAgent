import importlib

import geostructure


def test_package_imports_with_version():
    assert isinstance(geostructure.__version__, str)
    assert geostructure.__version__.count(".") == 2


def test_scientific_stack_is_available():
    for name in ["numpy", "scipy", "sympy", "pydantic", "h5py"]:
        importlib.import_module(name)
