import os

TEST_RUNS_LOCATION = os.environ.get("TEST_RUNS_LOCATION")

assert TEST_RUNS_LOCATION is not None

MONOMER_TEST_LOCATION = os.path.join(TEST_RUNS_LOCATION, "monomer_test")