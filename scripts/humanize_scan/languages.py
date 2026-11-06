"""Language-specific style rules."""

from __future__ import annotations

import ast
import re

from .core import Comment, FileAnalyzer, split_identifier


def analyze_language(fa: FileAnalyzer) -> None:
    if fa.lang == "python":
        analyze_python(fa)
    elif fa.lang == "javascript":
        analyze_javascript(fa)
    elif fa.lang == "php":
        analyze_php(fa)
    elif fa.lang in ("c", "cpp"):
        analyze_c_family(fa, fa.lang == "cpp")
    elif fa.lang == "java":
        analyze_java(fa)
    else:
        analyze_generic(fa)


def _line_of(source: str, pos: int) -> int:
    return source.count("\n", 0, pos) + 1


def _matches(
    fa: FileAnalyzer,
    rule: str,
    category: str,
    weight: int,
    message: str,
    pattern: str,
    *,
    text: str | None = None,
    cap: int = 3,
    flags: int = 0,
    risk: str = "low",
    sample_group: int = 0,
    fixable: bool = True,
) -> int:
    source = fa.masked if text is None else text
    count = 0
    for match in re.finditer(pattern, source, flags):
        count += 1
        line = _line_of(source, match.start()) if text is None else None
        sample = match.group(sample_group) if sample_group else match.group(0)
        fa.add(rule, category, weight, message, line, sample, cap=cap, risk=risk, fixable=fixable)
    return count


def _doc_stats(fa: FileAnalyzer) -> tuple[int, int]:
    docs = [
        c for c in fa.comments
        if c.kind == "block" and c.text.lstrip().startswith("/**")
    ]
    text = "\n".join(c.text for c in docs)
    tags = len(re.findall(r"@(?:param|return|returns|throws|brief|throws)\b", text, re.I))
    return len(docs), tags


def _add_doc_finding(
    fa: FileAnalyzer, rule: str, docs: int, tags: int, functions: int, language: str
) -> None:
    if docs >= 3 and functions >= 3 and docs / max(functions, 1) >= 0.5:
        fa.add(
            rule, "comments", 2,
            f"{language} doc block on most functions", None, cap=1,
        )
    if tags >= 5:
        fa.add(
            rule + "_FORMAL", "comments", 2,
            f"Formal {language} documentation tags on trivial interfaces", None, cap=1,
        )


# ---------------------------------------------------------------------------
# Python
# ---------------------------------------------------------------------------

def analyze_python(fa: FileAnalyzer) -> None:
    try:
        tree = ast.parse(fa.text)
    except SyntaxError as exc:
        fa.parse_error = f"{exc.msg} (line {exc.lineno})"
        fa.add(
            "PARSE_ERROR", "structure", 0,
            "Python parser could not read this file", exc.lineno, exc.msg,
            cap=1, fixable=False,
        )
        _python_regex_fallback(fa)
        return

    functions = [
        n for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    fa.context["function_count"] = len(functions)

    docstrings = 0
    formal_docs = 0
    annotated = 0
    total_args = 0
    has_return = 0
    long_functions: list[dict] = []
    function_names: dict[str, int] = {}
    call_counts: dict[str, int] = {}

    module_doc = ast.get_docstring(tree, clean=False)
    if module_doc:
        fa.comments.append(Comment(tree.body[0].lineno, module_doc, "docstring"))

    for node in functions:
        doc = ast.get_docstring(node, clean=False)
        if doc:
            docstrings += 1
            fa.comments.append(Comment(node.body[0].lineno, doc, "docstring"))
            low = doc.lower()
            formal = (
                low.lstrip().startswith(("this function", "this method", "this class", "this module"))
                or ("args:" in low and "returns:" in low)
                or len(doc.split()) >= 30
            )
            if formal:
                formal_docs += 1
                fa.add(
                    "PY_DOCSTRING_FORMAL", "comments", 2,
                    "Formal docstring restates the interface",
                    node.lineno, doc.splitlines()[0] if doc.splitlines() else doc,
                    cap=2,
                )
        total_args += len(node.args.args) + len(node.args.kwonlyargs)
        annotated += sum(1 for a in node.args.args + node.args.kwonlyargs if a.annotation is not None)
        if node.returns is not None:
            has_return += 1
            annotated += 1
        for default in list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                fa.add(
                    "PY_MUTABLE_DEFAULT", "legacy", -2,
                    "Mutable default argument", node.lineno, node.name,
                    cap=2, risk="medium",
                )
            elif isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id in ("list", "dict", "set"):
                fa.add(
                    "PY_MUTABLE_DEFAULT", "legacy", -2,
                    "Mutable default argument", node.lineno, node.name,
                    cap=2, risk="medium",
                )
        if re.search(r"[a-z][A-Z]", node.name) and not node.name.isupper():
            fa.add(
                "PY_CAMEL_FUNC", "legacy", -1,
                "CamelCase function name in Python", node.lineno, node.name, cap=2,
            )
        end = getattr(node, "end_lineno", node.lineno) or node.lineno
        if end - node.lineno > 80:
            long_functions.append({
                "name": node.name, "line": node.lineno, "length": end - node.lineno,
            })
        function_names[node.name] = node.lineno
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                call_counts[call.func.id] = call_counts.get(call.func.id, 0) + 1

    for node in classes:
        doc = ast.get_docstring(node, clean=False)
        if doc:
            fa.comments.append(Comment(node.body[0].lineno, doc, "docstring"))
            low = doc.lower()
            if low.lstrip().startswith(("this class", "this module")) or len(doc.split()) >= 30:
                formal_docs += 1
                fa.add(
                    "PY_DOCSTRING_FORMAL", "comments", 2,
                    "Formal class docstring restates the interface",
                    node.lineno, doc.splitlines()[0] if doc.splitlines() else doc,
                    cap=2,
                )

    if functions:
        if len(functions) >= 4 and docstrings / len(functions) >= 0.8 and formal_docs >= 1:
            fa.add(
                "PY_DOCSTRING_COVERAGE", "comments", 1,
                "Near-complete function docstring coverage", None, cap=1,
            )
        if len(functions) >= 3 and annotated / max(total_args + len(functions), 1) >= 0.8:
            fa.add(
                "PY_FULL_TYPE_HINTS", "structure", 1,
                "Exhaustive type annotations on a small module", None, cap=1,
            )

    for name, line in function_names.items():
        if len(name) >= 15 and call_counts.get(name, 0) == 1:
            node = next((n for n in functions if n.name == name), None)
            if node is not None and len(node.body) <= 6:
                fa.add(
                    "STRUCT_ONE_USE_HELPER", "structure", 1,
                    "Long-named helper with a single call site", line, name, cap=2,
                )

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    fa.add(
                        "PY_WILDCARD_IMPORT", "legacy", -2,
                        "Wildcard import", node.lineno,
                        f"from {node.module or ''} import *", cap=2, risk="medium",
                    )
        elif isinstance(node, ast.Import) and len(node.names) > 1:
            fa.add(
                "PY_MULTIPLE_IMPORTS", "legacy", -1,
                "Multiple imports on one line", node.lineno,
                ", ".join(a.name for a in node.names), cap=1,
            )
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            fa.add(
                "PY_PERCENT_FORMAT", "legacy", -1,
                "Percent-style string formatting", node.lineno,
                node.left.value[:80], cap=2,
            )
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            fa.add(
                "PY_DOT_FORMAT", "legacy", -1,
                ".format() string formatting", node.lineno, cap=2,
            )
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            fa.add(
                "PY_BARE_EXCEPT", "legacy", -2,
                "Bare except", node.lineno, cap=2, risk="medium",
            )
        elif isinstance(node, ast.ExceptHandler) and node.body and all(isinstance(b, ast.Pass) for b in node.body):
            fa.add(
                "PY_EXCEPT_PASS", "legacy", -2,
                "Except block silently passes", node.lineno, cap=2, risk="medium",
            )
        elif isinstance(node, ast.Compare):
            if any(isinstance(op, ast.Eq) for op in node.ops) and any(
                isinstance(c, ast.Constant) and c.value is None for c in node.comparators
            ):
                fa.add(
                    "PY_EQ_NONE", "legacy", -1,
                    "Comparison to None with ==", node.lineno, cap=1,
                )
        elif isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and any(isinstance(c, ast.Constant) and c.value == "__main__" for c in test.comparators)
            ):
                fa.add(
                    "PY_MAIN_GUARD", "structure", 0,
                    "Main guard is neutral", node.lineno, cap=1, fixable=False,
                )

    _matches(fa, "PY_OS_PATH", "legacy", -1, "os.path used instead of pathlib",
             r"\bos\.path\b", cap=1)
    _matches(fa, "PY_PRINT_DEBUG", "structure", -1, "print() left in source",
             r"\bprint\s*\(", cap=2)
    _matches(fa, "PY_FUTURE_IMPORTS", "structure", 1,
             "from __future__ import annotations", r"from\s+__future__\s+import\s+annotations",
             cap=1)
    _python_regex_fallback(fa)
    if long_functions:
        fa.context["long_functions"] = long_functions


def _python_regex_fallback(fa: FileAnalyzer) -> None:
    py2_patterns = (
        (r"(?m)^\s*print\s+[^(]", "print statement"),
        (r"\bxrange\s*\(", "xrange"),
        (r"\.iteritems\s*\(", "iteritems"),
        (r"\.has_key\s*\(", "has_key"),
        (r"\braw_input\s*\(", "raw_input"),
        (r"\bbasestring\b", "basestring"),
        (r"\bunicode\s*\(", "unicode()"),
    )
    for pattern, label in py2_patterns:
        if re.search(pattern, fa.masked):
            fa.add(
                "PY_PY2_SYNTAX", "legacy", -3,
                "Python 2 syntax or API", None, label, cap=2, risk="high",
            )
            break


# ---------------------------------------------------------------------------
# JavaScript / TypeScript
# ---------------------------------------------------------------------------

def analyze_javascript(fa: FileAnalyzer) -> None:
    masked = fa.masked
    function_kw = len(re.findall(r"\bfunction\b", masked))
    arrows = len(re.findall(r"=>", masked))
    methods = len(re.findall(r"(?m)^\s*(?:async\s+)?\w+\s*\([^;{}]*\)\s*\{", masked))
    functions = max(function_kw + arrows, methods)
    fa.context["function_count"] = functions

    _matches(fa, "JS_VAR", "legacy", -2, "var declaration", r"\bvar\s+", cap=3)
    _matches(fa, "JS_LOOSE_EQUAL", "legacy", -2, "Loose equality operator",
             r"(?<![=!<>])==(?!=)|(?<![=!<>])!=(?!=)", cap=2, risk="medium")
    _matches(fa, "JS_JQUERY", "legacy", -2, "jQuery usage",
             r"\$\s*\(|\bjQuery\s*\(", cap=2)
    _matches(fa, "JS_DOCUMENT_READY", "legacy", -1, "jQuery document.ready",
             r"\$\(\s*document\s*\)\.ready", cap=1)
    _matches(fa, "JS_AJAX", "legacy", -1, "jQuery ajax", r"\$\.ajax\s*\(", cap=1)
    _matches(fa, "JS_XHR", "legacy", -1, "XMLHttpRequest", r"\bnew\s+XMLHttpRequest\b", cap=1)
    _matches(fa, "JS_CONSOLE_LOG", "structure", -1, "Console logging left in source",
             r"\bconsole\.(?:log|debug|info)\s*\(", cap=2)
    _matches(fa, "JS_ALERT", "structure", -1, "alert() debug UI", r"\balert\s*\(", cap=1)
    _matches(fa, "JS_EVAL", "legacy", -3, "eval()", r"\beval\s*\(", cap=1, risk="high")
    _matches(fa, "JS_WITH", "legacy", -3, "with statement", r"\bwith\s*\(", cap=1, risk="high")
    _matches(fa, "JS_NEW_FUNCTION", "legacy", -3, "new Function()", r"\bnew\s+Function\s*\(", cap=1, risk="high")
    _matches(fa, "JS_DOCUMENT_WRITE", "legacy", -2, "document.write", r"\bdocument\.write\s*\(", cap=1, risk="medium")
    _matches(fa, "JS_INLINE_HANDLER", "legacy", -1, "Inline event handler",
             r"\bon(?:click|change|submit|load|mouseover|keyup)\s*=", cap=2)
    _matches(fa, "JS_PARSEINT_NO_RADIX", "legacy", -1, "parseInt without radix",
             r"\bparseInt\s*\(\s*[^,)]+\)", cap=2)
    _matches(fa, "JS_SUBSTR", "legacy", -1, "substr()", r"\.substr\s*\(", cap=2)
    _matches(fa, "JS_ARGUMENTS", "legacy", -1, "arguments object", r"\barguments\b", cap=1)
    _matches(fa, "JS_DEBUGGER", "structure", -2, "debugger statement", r"\bdebugger\b", cap=1)

    if function_kw >= 4 and arrows == 0 and fa.loc >= 50:
        fa.add(
            "JS_FUNCTION_STYLE", "structure", -1,
            "Function-only style; older but valid", None, cap=1,
        )

    docs, tags = _doc_stats(fa)
    _add_doc_finding(fa, "JS_JSDOC", docs, tags, functions, "JSDoc")

    declarations = len(re.findall(r"\b(?:const|let)\s+", masked))
    if declarations >= 3 and len(re.findall(r"\bvar\s+", masked)) == 0:
        fa.add("JS_MODERN_DECL", "structure", 1, "const/let throughout", None, cap=1)
    if arrows >= 3:
        fa.add("JS_ARROW", "structure", 1, "Arrow functions throughout", None, cap=1)
    if len(re.findall(r"\basync\b", masked)) >= 2 and len(re.findall(r"\bawait\b", masked)) >= 2:
        fa.add("JS_ASYNC_AWAIT", "structure", 1, "async/await throughout", None, cap=1)
    if len(re.findall(r"\?\.", masked)) + len(re.findall(r"\?\?", masked)) >= 2:
        fa.add("JS_OPTIONAL_CHAINING", "structure", 1, "Optional chaining / nullish coalescing", None, cap=1)
    strict = len(re.findall(r"===", masked))
    loose = len(re.findall(r"(?<![=!<>])==(?!=)|(?<![=!<>])!=(?!=)", masked))
    if strict >= 3 and loose == 0:
        fa.add("JS_STRICT_EQUALITY", "structure", 1, "Strict equality throughout", None, cap=1)
    if masked.count("`") >= 4:
        fa.add("JS_TEMPLATE_LITERALS", "structure", 1, "Template literals throughout", None, cap=1)
    if fa.path.endswith((".ts", ".tsx")):
        fa.add("JS_TYPESCRIPT", "structure", 0, "TypeScript file", None, cap=1, fixable=False)


# ---------------------------------------------------------------------------
# PHP
# ---------------------------------------------------------------------------

def analyze_php(fa: FileAnalyzer) -> None:
    masked = fa.masked
    functions = len(re.findall(r"\bfunction\s+\w+\s*\(", masked))
    fa.context["function_count"] = functions

    if re.search(r"<\?(?!php|=|xml)", masked):
        fa.add("PHP_SHORT_TAG", "legacy", -2, "PHP short open tag", None, cap=1, risk="medium")
    _matches(fa, "PHP_SHORT_ECHO", "legacy", -1, "Short echo tag", r"<\?=", text=fa.text, cap=1)
    _matches(fa, "PHP_MYSQL", "legacy", -3, "Removed mysql_* API",
             r"\bmysql_\w+\s*\(", cap=2, risk="high")
    _matches(fa, "PHP_EREG", "legacy", -2, "Removed ereg API", r"\bereg\w*\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_SPLIT", "legacy", -2, "Removed split()", r"\bsplit\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_EACH", "legacy", -2, "Removed each()", r"\beach\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_CREATE_FUNCTION", "legacy", -3, "Removed create_function()",
             r"\bcreate_function\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_MCRYPT", "legacy", -3, "Removed mcrypt_* API",
             r"\bmcrypt_\w+\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_GLOBAL", "legacy", -2, "global variable", r"\bglobal\s+\$", cap=2)
    _matches(fa, "PHP_REQUEST", "legacy", -1, "$_REQUEST used", r"\$_REQUEST\b", cap=1, risk="medium")
    _matches(fa, "PHP_EXTRACT", "legacy", -3, "extract()", r"\bextract\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_EVAL", "legacy", -3, "eval()", r"\beval\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_OR_DIE", "legacy", -2, "or die()", r"\bor\s+die\s*\(", cap=1)
    _matches(fa, "PHP_DIE", "legacy", -1, "die()/exit()", r"\b(?:die|exit)\s*\(", cap=1)
    _matches(fa, "PHP_OLD_ARRAY", "legacy", -1, "array() syntax", r"\barray\s*\(", cap=2)
    _matches(fa, "PHP_VAR_KEYWORD", "legacy", -1, "PHP 4 var property", r"\bvar\s+\$", cap=1)
    _matches(fa, "PHP_MD5", "legacy", -3, "Weak hash (md5/sha1)", r"\b(?:md5|sha1)\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_RAND", "legacy", -1, "rand() for values", r"\brand\s*\(", cap=1)
    _matches(fa, "PHP_ADD_SLASHES", "legacy", -2, "addslashes()", r"\baddslashes\s*\(", cap=1, risk="high")
    _matches(fa, "PHP_ERROR_SUPPRESSION", "legacy", -2, "Error suppression with @",
             r"@\w+", cap=2, risk="medium")
    _matches(fa, "PHP_DEBUG_OUTPUT", "structure", -1, "Debug output left in source",
             r"\b(?:var_dump|print_r|error_log)\s*\(", cap=2)

    for match in re.finditer(r"header\s*\(\s*['\"]Location:", masked):
        line = _line_of(masked, match.start())
        window = "\n".join(fa.lines[line - 1:line + 3])
        if not re.search(r"\b(?:exit|die)\s*\(", window):
            fa.add(
                "PHP_HEADER_REDIRECT", "legacy", -2,
                "Redirect without exit/die", line, match.group(0),
                cap=2, risk="medium",
            )

    if fa.text.rstrip().endswith("?>"):
        fa.add("PHP_CLOSING_TAG", "legacy", -1, "Closing PHP tag at end of file", None, cap=1)

    if re.search(r"\bclass\s+\w+", masked):
        for match in re.finditer(r"(?m)^\s*function\s+\w+\s*\(", masked):
            prefix = masked[max(0, match.start() - 24):match.start()]
            if not re.search(r"\b(public|private|protected)\b", prefix):
                fa.add(
                    "PHP_NO_VISIBILITY", "legacy", -1,
                    "Method without explicit visibility",
                    _line_of(masked, match.start()), match.group(0).strip(), cap=2,
                )

    docs, tags = _doc_stats(fa)
    _add_doc_finding(fa, "PHP_DOCBLOCK", docs, tags, functions, "PHPDoc")

    if re.search(r"declare\s*\(\s*strict_types\s*=\s*1\s*\)", masked):
        fa.add("PHP_STRICT_TYPES", "structure", 1, "strict_types enabled", None, cap=1)
    if re.search(r"(?m)^\s*namespace\s+", masked):
        fa.add("PHP_NAMESPACE", "structure", 1, "Namespace used", None, cap=1)
    if re.search(r"->prepare\s*\(", masked):
        fa.add("PHP_PREPARED", "structure", 1, "Prepared statements used", None, cap=1)
    if re.search(r"function\s+\w+\s*\([^)]*\)\s*:\s*\??\w+", masked):
        fa.add("PHP_RETURN_TYPES", "structure", 1, "Return types declared", None, cap=1)

    if re.search(r"<html|<div|<form|<table", fa.text, re.I):
        fa.add(
            "PHP_INLINE_HTML", "legacy", 0,
            "Mixed HTML and PHP; neutral in legacy templates", None, cap=1,
            fixable=False,
        )


# ---------------------------------------------------------------------------
# C / C++
# ---------------------------------------------------------------------------

def analyze_c_family(fa: FileAnalyzer, is_cpp: bool) -> None:
    masked = fa.masked
    cpp_mode = is_cpp or bool(re.search(r"\bstd::|\bclass\s+\w+|\bnamespace\s+\w+", masked))
    functions = len(re.findall(
        r"(?m)^[ \t]*(?:static\s+|inline\s+|extern\s+|const\s+|unsigned\s+|signed\s+|struct\s+\w+\s+|enum\s+\w+\s+)*"
        r"[A-Za-z_]\w*[\w\s\*&:<>,]*\s+[A-Za-z_]\w*\s*\([^;{}]*\)\s*(?:const\s*)?\{",
        masked,
    ))
    fa.context["function_count"] = functions

    _matches(fa, "C_NULL", "legacy", -1, "NULL macro", r"\bNULL\b", cap=2)
    _matches(fa, "C_MALLOC", "legacy", -1, "malloc/free ownership",
             r"\b(?:malloc|calloc|realloc|free)\s*\(", cap=2)
    _matches(fa, "C_UNSAFE_STR", "legacy", -2, "Unsafe string function",
             r"\b(?:gets|strcpy|strcat|sprintf|scanf)\s*\(", cap=2, risk="high")
    _matches(fa, "C_TYPEDEF_STRUCT", "legacy", -1, "typedef struct",
             r"\btypedef\s+struct\b", cap=1)
    _matches(fa, "C_REGISTER", "legacy", -1, "register keyword", r"\bregister\s+", cap=1)
    _matches(fa, "C_USING_NAMESPACE", "legacy", -2, "using namespace std",
             r"\busing\s+namespace\s+std\s*;", cap=1, risk="medium")
    _matches(fa, "C_ENDL", "legacy", -1, "std::endl flushes", r"\bstd::endl\b|\bendl\b", cap=2)
    _matches(fa, "C_NEW_DELETE", "legacy", -1, "Raw new/delete",
             r"\b(?:new|delete)\b", cap=2)
    _matches(fa, "C_C_STYLE_CAST", "legacy", -1, "C-style cast",
             r"\([A-Za-z_]\w*\s*\*?\)\s*[A-Za-z_]\w*", cap=1, risk="medium")
    _matches(fa, "C_DEBUG_PRINT", "structure", -1, "Debug print left in source",
             r"\b(?:printf|std::cout|cout)\s*(?:\(|<<)", cap=2)
    _matches(fa, "C_AUTHOR_DATE", "comments", -1, "Author/date comment",
             r"\b(?:author|created|date|modified)\s*:", text="\n".join(c.text for c in fa.comments),
             cap=1)
    _matches(fa, "C_HUNGARIAN", "naming", -1, "Hungarian or prefix notation",
             r"\b(?:g_|s_|m_|k[A-Z]|(?:dw|sz|lp|h|b|n|p|w|d|f|ch|by|i|u|l|ul|ll|ull)[A-Z][a-z])",
             cap=1)
    _matches(fa, "C_PRAGMA_ONCE", "structure", 0, "#pragma once is neutral",
             r"#pragma\s+once", cap=1, fixable=False)

    docs, tags = _doc_stats(fa)
    _add_doc_finding(fa, "C_DOXYGEN", docs, tags, functions, "Doxygen")

    if cpp_mode:
        _matches(fa, "C_NULLPTR", "structure", 1, "nullptr used", r"\bnullptr\b", cap=1)
        _matches(fa, "C_SMART_POINTER", "structure", 1, "Smart pointer used",
                 r"\b(?:unique_ptr|shared_ptr|weak_ptr|make_unique|make_shared)\b", cap=1)
        _matches(fa, "C_AUTO", "structure", 1, "auto used", r"\bauto\b", cap=1)
        _matches(fa, "C_RANGE_FOR", "structure", 1, "Range-based for",
                 r"\bfor\s*\([^;:]*:[^;]*\)", cap=1)
        _matches(fa, "C_OVERRIDE", "structure", 1, "override used", r"\boverride\b", cap=1)
        _matches(fa, "C_ENUM_CLASS", "structure", 1, "enum class used", r"\benum\s+class\b", cap=1)
        _matches(fa, "C_STATIC_CAST", "structure", 1, "static_cast used", r"\bstatic_cast\s*<", cap=1)


# ---------------------------------------------------------------------------
# Java
# ---------------------------------------------------------------------------

def analyze_java(fa: FileAnalyzer) -> None:
    masked = fa.masked
    functions = len(re.findall(
        r"(?m)^[ \t]*(?:@\w+\s*)*(?:public|private|protected|static|final|abstract|"
        r"synchronized|native|default|strictfp|[\w<>\[\],.?]+)\s+"
        r"[\w<>\[\],.?]+\s*\([^;{}]*\)\s*(?:throws\s+[\w, .]+)?\{",
        masked,
    ))
    fa.context["function_count"] = functions

    _matches(fa, "JAVA_SYSTEM_OUT", "structure", -1, "System.out/err output",
             r"\bSystem\.(?:out|err)\.print", cap=2)
    _matches(fa, "JAVA_PRINT_STACK", "structure", -2, "printStackTrace()",
             r"\.printStackTrace\s*\(", cap=2)
    _matches(fa, "JAVA_LEGACY_COLLECTION", "legacy", -2, "Legacy collection type",
             r"\b(?:Vector|Hashtable|Enumeration|Stack)\b", cap=2, risk="medium")
    _matches(fa, "JAVA_DATE_CALENDAR", "legacy", -1, "Date/Calendar API",
             r"\b(?:Date|Calendar|SimpleDateFormat)\b", cap=2)
    _matches(fa, "JAVA_RAW_TYPE", "legacy", -2, "Raw generic type",
             r"\b(?:List|Map|Set|Collection|ArrayList|HashMap)\s+[A-Za-z_]\w*\s*=",
             cap=2, risk="medium")
    _matches(fa, "JAVA_WILDCARD_IMPORT", "legacy", -1, "Wildcard import",
             r"(?m)^\s*import\s+[\w.]+\.\*", cap=2)
    _matches(fa, "JAVA_FINALIZE", "legacy", -3, "finalize()", r"\bfinalize\s*\(", cap=1, risk="high")
    _matches(fa, "JAVA_THREAD_STOP", "legacy", -3, "Thread.stop()", r"\.stop\s*\(", cap=1, risk="high")
    _matches(fa, "JAVA_RUNTIME_EXEC", "legacy", -2, "Runtime.exec()",
             r"\bRuntime\.getRuntime\s*\(\s*\)\.exec\s*\(", cap=1, risk="medium")
    _matches(fa, "JAVA_TRY_FINALLY", "legacy", -1, "Manual close in finally",
             r"finally\s*\{[^}]*\.close\s*\(", cap=1)
    _matches(fa, "JAVA_ANONYMOUS_CLASS", "legacy", -1, "Anonymous inner class",
             r"\bnew\s+\w+(?:<[^>]+>)?\s*\(\s*\)\s*\{", cap=1)

    getters = len(re.findall(r"\b(?:get|set|is)[A-Z]\w*\s*\(", masked))
    if getters >= 8 and fa.loc >= 60:
        fa.add(
            "JAVA_GETTER_SETTER", "structure", 1,
            "Large number of getters/setters", None, cap=1,
        )

    docs, tags = _doc_stats(fa)
    _add_doc_finding(fa, "JAVA_JAVADOC", docs, tags, functions, "Javadoc")

    modern_patterns = (
        ("JAVA_STREAMS", r"\.stream\s*\(|->", "Streams/lambdas"),
        ("JAVA_OPTIONAL", r"\bOptional\s*<", "Optional used"),
        ("JAVA_RECORDS", r"(?m)^\s*(?:public\s+)?record\s+\w+", "record used"),
        ("JAVA_VAR", r"\bvar\s+\w+\s*=", "var used"),
        ("JAVA_FACTORY_METHODS", r"\b(?:List|Map|Set)\.of\s*\(", "List.of/Map.of/Set.of"),
        ("JAVA_TIME", r"\b(?:java\.time|LocalDate|LocalDateTime|Instant)\b", "java.time used"),
        ("JAVA_TRY_RESOURCES", r"\btry\s*\(", "try-with-resources"),
        ("JAVA_OVERRIDE", r"@Override\b", "@Override used"),
        ("JAVA_REQUIRE_NONNULL", r"\bObjects\.requireNonNull\s*\(", "Objects.requireNonNull"),
        ("JAVA_DI", r"@(?:Autowired|Inject|Service|Component|Repository)\b", "DI annotation"),
    )
    for rule, pattern, label in modern_patterns:
        if re.search(pattern, masked):
            fa.add(rule, "structure", 1, label, None, cap=1)


def analyze_generic(fa: FileAnalyzer) -> None:
    functions = len(re.findall(
        r"\b(?:def|function|func|fn|fun|sub|proc)\s+\w+", fa.masked
    ))
    fa.context["function_count"] = functions
    fa.add(
        "GEN_FALLBACK", "structure", 0,
        f"No language-specific rules for {fa.lang}; score is weaker evidence",
        None, cap=1, fixable=False,
    )
