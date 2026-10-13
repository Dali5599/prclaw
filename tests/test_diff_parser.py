"""Tests for PRClaw diff parser module."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff, parse_unified_diff


def test_parse_empty_diff():
    assert parse_unified_diff("") == []
    assert parse_unified_diff("   \n  ") == []


def test_parse_single_file_single_hunk():
    sample_diff = """diff --git a/src/hello.py b/src/hello.py
index e69de29..49983de 100644
--- a/src/hello.py
+++ b/src/hello.py
@@ -1,3 +1,4 @@
 def hello():
-    return "old"
+    # Updated greeting
+    return "new"
"""
    files = parse_unified_diff(sample_diff)
    assert len(files) == 1
    f = files[0]
    assert f.old_path == "src/hello.py"
    assert f.new_path == "src/hello.py"
    assert not f.is_new
    assert not f.is_deleted
    assert len(f.hunks) == 1

    hunk = f.hunks[0]
    assert hunk.old_start == 1
    assert hunk.old_lines == 3
    assert hunk.new_start == 1
    assert hunk.new_lines == 4
    assert len(hunk.added_lines) == 2
    assert hunk.added_lines == ["    # Updated greeting", "    return \"new\""]
    assert len(hunk.removed_lines) == 1
    assert hunk.removed_lines == ["    return \"old\""]


def test_parse_new_file_and_deletion():
    sample = """diff --git a/new.txt b/new.txt
new file mode 100644
--- /dev/null
+++ b/new.txt
@@ -0,0 +1,2 @@
+line 1
+line 2
diff --git a/old.txt b/old.txt
deleted file mode 100644
--- a/old.txt
+++ /dev/null
@@ -1,1 +0,0 @@
-deleted line
"""
    files = parse_unified_diff(sample)
    assert len(files) == 2
    assert files[0].is_new is True
    assert files[0].target_path == "new.txt"
    assert len(files[0].hunks) == 1
    assert files[0].hunks[0].added_lines == ["line 1", "line 2"]

    assert files[1].is_deleted is True
    assert files[1].target_path == "old.txt"
    assert len(files[1].hunks) == 1
    assert files[1].hunks[0].removed_lines == ["deleted line"]
