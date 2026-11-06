from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from humanize_scan.report import scan_path, write_reports  # noqa: E402


PY_AI = '''\
def calculate_total_price_with_tax(order_items):
    """This function calculates the total price with tax.

    Args:
        order_items: The list of order items.

    Returns:
        The total price including tax.
    """
    total_price = 0.0
    for order_item in order_items:
        total_price += order_item.price * (1 + order_item.tax_rate)
    return total_price
'''

PY_HUMAN = '''\
from os import *

def total(items):
    # TODO: handle the tax edge case
    total = 0
    for i in items:
        total += i.price
    print("%s items" % len(items))
    return total
'''

JS_LEGACY = '''\
var count = 0;
$(".btn").click(function () {
  if (count == 0) {
    console.log("clicked");
  }
});
'''

PHP_LEGACY = '''\
<?
global $db;
$id = $_REQUEST['id'];
$result = mysql_query("SELECT * FROM users WHERE id = " . $id);
?>
'''

CPP_LEGACY = '''\
#include <stdlib.h>
#include <string.h>

UserInfo* getUser(int id) {
    UserInfo* p = (UserInfo*)malloc(sizeof(UserInfo));
    if (p == NULL) return NULL;
    strcpy(p->name, "x");
    return p;
}
'''

JAVA_LEGACY = '''\
import java.util.*;

public class Users {
    Vector users = new Vector();

    public void printUsers() {
        System.out.println(users);
    }
}
'''


class ScannerTests(unittest.TestCase):
    def analyze_one(self, name: str, text: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            scan = scan_path(path)
            self.assertEqual(scan["summary"]["files"], 1)
            return scan["files"][0]

    def rules(self, report: dict) -> set[str]:
        return {f["rule"] for f in report["findings"] if f["count"] > 0}

    def test_python_ai_signals(self) -> None:
        report = self.analyze_one("sample.py", PY_AI)
        rules = self.rules(report)
        self.assertIn("NAME_VERY_LONG", rules)
        self.assertIn("PY_DOCSTRING_FORMAL", rules)

    def test_python_human_signals(self) -> None:
        report = self.analyze_one("sample.py", PY_HUMAN)
        rules = self.rules(report)
        self.assertIn("PY_WILDCARD_IMPORT", rules)
        self.assertIn("PY_PERCENT_FORMAT", rules)
        self.assertIn("COMMENT_TODO", rules)

    def test_javascript_legacy_signals(self) -> None:
        report = self.analyze_one("sample.js", JS_LEGACY)
        rules = self.rules(report)
        for rule in ("JS_VAR", "JS_LOOSE_EQUAL", "JS_JQUERY", "JS_CONSOLE_LOG"):
            self.assertIn(rule, rules)

    def test_php_legacy_signals(self) -> None:
        report = self.analyze_one("sample.php", PHP_LEGACY)
        rules = self.rules(report)
        for rule in ("PHP_SHORT_TAG", "PHP_GLOBAL", "PHP_MYSQL", "PHP_CLOSING_TAG"):
            self.assertIn(rule, rules)

    def test_cpp_legacy_signals(self) -> None:
        report = self.analyze_one("sample.cpp", CPP_LEGACY)
        rules = self.rules(report)
        for rule in ("C_NULL", "C_MALLOC", "C_UNSAFE_STR", "C_C_STYLE_CAST"):
            self.assertIn(rule, rules)

    def test_java_legacy_signals(self) -> None:
        report = self.analyze_one("Users.java", JAVA_LEGACY)
        rules = self.rules(report)
        for rule in ("JAVA_WILDCARD_IMPORT", "JAVA_LEGACY_COLLECTION", "JAVA_SYSTEM_OUT"):
            self.assertIn(rule, rules)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "a.py").write_text(PY_AI, encoding="utf-8")
            (root / "b.js").write_text(JS_LEGACY, encoding="utf-8")
            out = Path(tmp) / "out"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_style.py"), str(root),
                 "--out", str(out), "--quiet"],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            data = json.loads((out / "scan.json").read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["files"], 2)
            self.assertTrue((out / "scan.md").exists())

    def test_cli_json_only_and_language_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "a.py").write_text(PY_AI, encoding="utf-8")
            (root / "b.js").write_text(JS_LEGACY, encoding="utf-8")
            out = Path(tmp) / "out"
            subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_style.py"), str(root),
                 "--out", str(out), "--lang", "python", "--json-only", "--quiet"],
                check=True, capture_output=True, text=True,
            )
            data = json.loads((out / "scan.json").read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["files"], 1)
            self.assertEqual(data["files"][0]["language"], "python")
            self.assertFalse((out / "scan.md").exists())

    def test_scan_path_excludes_vendor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "src").mkdir(parents=True)
            (root / "vendor").mkdir()
            (root / "src" / "ok.py").write_text(PY_HUMAN, encoding="utf-8")
            (root / "vendor" / "skip.py").write_text(PY_AI, encoding="utf-8")
            scan = scan_path(root)
            self.assertEqual(scan["summary"]["files"], 1)
            self.assertEqual(scan["files"][0]["path"], "src/ok.py")


if __name__ == "__main__":
    unittest.main()
