"just create typeshed stubs"
from get_all_frozen import make_stub_files
def just_stub(levels):
    make_stub_files('./stubs', levels)

if __name__ == "__main__":
    just_stub(7)
