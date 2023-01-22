import sys
import os.path as osp

# Make sure that the application source directory (this directory's parent) is
# on sys.path.
print("opa")
here = osp.join(osp.dirname(osp.abspath(__file__)), osp.pardir, "src")
sys.path.insert(0, here)