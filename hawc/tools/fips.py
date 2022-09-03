# TODO - remove module after django>=4.1 -> https://github.com/django/django/pull/14763/
import os
import hashlib
import importlib


def _non_security_md5(*args, **kwargs):
    kwargs["usedforsecurity"] = False
    return hashlib.md5(*args, **kwargs)


def monkey_patch_md5(modules_to_patch):
    """Monkey-patch calls to MD5 that aren't used for security purposes.

    Sets RHEL's custom flag `usedforsecurity` to False allowing MD5 in FIPS mode.
    `modules_to_patch` must be an iterable of module names (strings).
    Modules must use `import hashlib` and not `from hashlib import md5`.
    """
    # Manually load a module as a unique instance
    # https://stackoverflow.com/questions/11170949/
    HASHLIB_SPEC = importlib.util.find_spec("hashlib")
    patched_hashlib = importlib.util.module_from_spec(HASHLIB_SPEC)
    HASHLIB_SPEC.loader.exec_module(patched_hashlib)

    patched_hashlib.md5 = _non_security_md5

    # Inject our patched_hashlib for all requested modules
    for module_name in modules_to_patch:
        module = importlib.import_module(module_name)
        module.hashlib = patched_hashlib


def patch_md5():
    run_once = os.environ.get("HAWC_RUN_ONCE")
    if run_once is not None:
        return
    os.environ["HAWC_RUN_ONCE"] = "True"
    print("FIPS monkeypatch enabled...")
    monkey_patch_md5(
        [
            "django.contrib.staticfiles.storage",
            "django.core.cache.backends.filebased",
            "django.core.cache.utils",
            "django.db.backends.utils",
            "django.utils.cache",
        ]
    )
