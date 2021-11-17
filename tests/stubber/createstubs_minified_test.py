import sys
from collections import namedtuple
import pytest

from pathlib import Path

core_mocks = "./tests/mocks/micropython-cpython_core"

# def setup_module(module):
#     print("\nsetup_module()")


def teardown_module(module):
    print("teardown_module()")
    # remove mocks from path
    if core_mocks in sys.path:
        sys.path.remove(core_mocks)


UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])

# allow loading of the cpython mock-a-likes
if not core_mocks in sys.path:
    sys.path[1:1] = [core_mocks]

# ----------------------------------------------------------------------------------------
# Specify wether to load the normal or minified version of the test
# ----------------------------------------------------------------------------------------

# Allow test discovery even if the minified version does not exist or has errors
try:
    prefix = "minified."
    from minified.createstubs import Stubber, read_path
    import minified.createstubs as createstubs
except Exception:
    createstubs = Stubber = read_path = None


# ----------------------------------------------------------------------------------------
# Below this the tests are identical between :
# - createstubs_board.test.py
# - createstubs_minified.test.py
# ----------------------------------------------------------------------------------------


@pytest.mark.minified
def test_stubber_Class_available():
    assert Stubber is not None, "Stubber Class not imported"


@pytest.mark.minified
def test_stubber_info_basic():
    stubber = Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    info = createstubs._info()
    print(info)
    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["port"] != "", "stubber.info() - No port detected"
    assert info["platform"] != "", "stubber.info() - No platform detected"
    assert info["ver"] != "", "stubber.info() - No clean version detected"

    assert stubber._fwid != "none"

    assert " " not in stubber.flat_fwid, "flat_fwid must not contain any spaces"
    assert "." not in stubber.flat_fwid, "flat_fwid must not contain any dots"


@pytest.mark.minified
def test_stubber_info_custom():
    myid = "MyCustomID"
    stubber = Stubber(firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    assert stubber._fwid != "none"
    assert stubber._fwid == myid.lower()


#################################################
# test the fwid naming on the different platforms
#################################################
from testcases import fwid_test_cases


@pytest.mark.parametrize("fwid,  sys_imp_name, sys_platform, os_uname", fwid_test_cases)
@pytest.mark.minified
def test_stubber_fwid(mocker, fwid, sys_imp_name, sys_platform, os_uname):
    # class.property : just pass a value
    mocker.patch(prefix + "createstubs.sys.platform", sys_platform)
    mocker.patch(prefix + "createstubs.sys.implementation.name", sys_imp_name)
    # class.method--> mock using function
    fake_uname = os_uname

    def mock_uname():
        return fake_uname

    mocker.patch(prefix + "createstubs.os.uname", mock_uname, create=True)
    # now run the tests
    stubber = Stubber()
    assert stubber is not None, "Can't create Stubber instance"

    info = createstubs._info()
    print("\nvalidating: " + fwid)
    print(info)

    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["port"] != "", "stubber.info() - No port detected"
    assert info["platform"] != "", "stubber.info() - No platform detected"
    assert info["ver"] != "", "stubber.info() - No clean version detected"

    assert stubber._fwid != "none"

    # Does the firmware id match
    assert stubber._fwid == fwid

    chars = " .()/\\:$"
    for c in chars:
        assert c not in stubber.flat_fwid, "flat_fwid must not contain '{}'".format(c)


# throws an error on the commandline
@pytest.mark.minified
@pytest.mark.skip(reason="test not working")
def test_read_path():
    assert read_path() == ""


@pytest.mark.minified
def test_get_obj_attributes():
    stubber = Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    items, errors = stubber.get_obj_attributes(sys)
    assert items != []
    assert errors == []
    assert len(items) > 50
    for attr in items:
        assert type(attr) == tuple


@pytest.mark.minified
def test_create_all_stubs(tmp_path: Path):
    myid = "MyCustomID"

    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.modules = ["json", "_thread", "array"]
    stubber.add_modules(["http_client", "webrepl", "_internal"])
    stubber.create_all_stubs()

    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 3
    stubber.report()
    stublist = list(tmp_path.glob("**/modules.json"))
    assert len(stublist) == 1

    stubber.clean()
    stublist = list(tmp_path.glob("**/*.*"))
    assert len(stublist) == 0


@pytest.mark.minified
def test_get_root():
    x = createstubs.get_root()
    assert type(x) == str
    assert len(x) > 0


@pytest.mark.minified
def test_create_module_stub(tmp_path: Path):
    myid = "MyCustomID"
    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # just in the test folder , no structure
    stubber.create_module_stub("json", str(tmp_path / "json.py"))
    stubber.create_module_stub("_thread", str(tmp_path / "_thread.py"))

    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 2


@pytest.mark.minified
def test_create_module_stub_folder(tmp_path: Path):
    myid = "MyCustomID"
    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    stubber.create_module_stub("json")
    stublist = list((tmp_path / "stubs" / myid.lower()).glob("**/*.py"))
    assert len(stublist) == 1, "should create stub in stub folder if no folder specified"


@pytest.mark.minified
def test_create_module_stub_ignored(tmp_path: Path):
    myid = "MyCustomID"
    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # should not generate
    stubber.create_module_stub("_internal", str(tmp_path / "_internal.py"))
    stubber.create_module_stub("http_client", str(tmp_path / "http_client.py"))
    stubber.create_module_stub("webrepl", str(tmp_path / "webrepl.py"))

    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 0


@pytest.mark.minified
def test_nested_modules(tmp_path: Path):
    myid = "MyCustomID"
    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # just in the test folder , no structure
    stubber.create_module_stub("urllib/request", str(tmp_path / "request.py"))
    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 1


@pytest.mark.minified
def test_unavailable_modules(tmp_path: Path):
    myid = "MyCustomID"
    stubber = Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # this should not generate a module , but also should not th
    stubber.create_module_stub("notamodule1", str(tmp_path / "notamodule1.py"))
    stubber.create_module_stub("not/amodule2", str(tmp_path / "notamodule2.py"))
    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 0


# def test_clean(tmp_path):

#     myid = "MyCustomID"
#     test_path = str(tmp_path)
#     stub_path =  Path(test_path) /"stubs"/ myid.lower()
#     stubber = Stubber(path = test_path, firmware_id=myid)
#     stubber.clean()

#     #Create a file
#     stubber.create_module_stub("json", PurePosixPath( stub_path / "json.py") )
#     stublist = list(Path(test_path).glob('**/*.py'))
#     assert len(stublist) == 1
#     stubber.clean()
# Error
# # tests\stubber\createstubs_info_mpy_test.py:244:
# # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
# # board\createstubs.py:435: in create_module_stub
# #     with open(file_name, "w") as fp:
# # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

# # name = PurePosixPath('C:\\/Users/josverl/AppData/Local/Temp/pytest-of-josverl/pytest-39/test_clean0/stubs/mycustomid/json.py')
# # mode = 'w', args = (), kw = {}

# #     def open(name, mode="r", *args, **kw):
# # >       f = io.open(name, mode, *args, **kw)
# # E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\/Users/josverl/AppData/Local/Temp/pytest-of-josverl/pytest-39/test_clean0/stubs/mycustomid/json.py'

# # tests\mocks\micropython-cpython_core\uio.py:44: FileNotFoundError
