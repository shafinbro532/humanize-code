"""Core data structures, masking, metrics, and common style rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

EXT_LANG = {
    ".py": "python", ".pyw": "python", ".pyi": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".cjs": "javascript", ".ts": "javascript", ".tsx": "javascript",
    ".php": "php", ".phtml": "php", ".php3": "php", ".php4": "php",
    ".php5": "php", ".inc": "php",
    ".c": "c", ".h": "c",
    ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".c++": "cpp",
    ".hpp": "cpp", ".hh": "cpp", ".hxx": "cpp", ".ipp": "cpp",
    ".java": "java",
    ".go": "generic", ".rs": "generic", ".rb": "generic", ".cs": "generic",
    ".kt": "generic", ".kts": "generic", ".swift": "generic", ".sh": "generic",
    ".bash": "generic", ".ps1": "generic", ".sql": "generic", ".lua": "generic",
    ".pl": "generic", ".r": "generic", ".scala": "generic", ".dart": "generic",
    ".ex": "generic", ".exs": "generic", ".erl": "generic", ".hs": "generic",
    ".clj": "generic", ".vue": "generic", ".svelte": "generic", ".astro": "generic",
}

DEFAULT_SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".vs", ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    "node_modules", "bower_components", "jspm_packages", "vendor", "third_party",
    "Pods", "Carthage", "dist", "build", "out", "target", "bin", "obj",
    "coverage", ".next", ".nuxt", ".cache", ".gradle", ".terraform",
    "humanize-out", "htmlcov", ".pytest_tmp",
}

SKIP_FILE_PATTERNS = (
    "*.min.js", "*.min.css", "*.map", "*.lock", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", "composer.lock", "*.generated.*",
    "*_generated.*", "*.g.dart", "*.designer.cs", "*.pb.go", "*.pb.cc",
    "*.pb.h", "*.snap",
)

DEFAULT_LINE_LIMITS = {
    "python": 79, "javascript": 100, "php": 120, "c": 100, "cpp": 100,
    "java": 120, "generic": 100,
}

KEYWORDS = set("""
abstract alias and args as assert async await auto bool boolean break byte
case catch char class const continue debugger def default defer del delegate
delete do double dynamic echo else elseif end enum event explicit export extends
extern false final finally fixed float fn for foreach friend from func function
global go goto if implements implicit import in include instanceof int interface
internal is lambda let lock long module namespace native new nil no not null
object of on operator or out override package params private protected public
raise readonly record ref register reinterpret_cast require return sbyte sealed
select short signed sizeof static strictfp string struct super switch synchronized
template this throw throws trait transient true try typedef typename typeof uint
ulong unchecked union unsafe unsigned use using var virtual void volatile when
where while with yield None True False
""".split())

BUILTINS = set("""
__init__ __main__ __name__ self cls super none true false null nil undefined nan inf
print len range list dict set tuple str int float bool bytes bytearray object
type isinstance issubclass hasattr getattr setattr delattr vars dir id hash
iter next map filter zip enumerate sorted reversed sum min max abs round open
input format repr all any chr ord hex oct bin pow divmod
console window document module exports require process global
array echo empty isset unset die exit
""".split())

NOISE_IDENTIFIERS = set("""
excepthandler argumentparser stringbuilder bufferedreader inputstream
outputstream arraylist hashmap linkedlist hashset treeset exception
runtimeexception illegalargumentexception nullpointerexception
filenotfoundexception
""".split())

STRING_PREFIXES = {"f", "r", "b", "u", "br", "rb", "fr", "rf"}

ABBREV = set("""
req res resp cfg ctx idx msg err tmp buf len src dst cb fn val obj str num usr
pwd btn img nav ptr ref opts args params attrs env db mgr svc pref prev cur curr
dest elem el evt ev fh fd pid uid gid uuid guid ip tcp udp tls ssl jwt otp mfa 2fa
""".split())

ENTERPRISE_TOKENS = set("""
manager service controller repository factory strategy provider handler processor
coordinator orchestrator facade adapter wrapper implementation initializer
functionality infrastructure abstraction utility utilities validator transformer
serializer deserializer middleware dispatcher listener observer registry resolver
builder locator gateway delegate interceptor dto dao impl supervisor director
""".split())

GENERIC_TOKENS = set("""
information data configuration implementation functionality object value result
response request collection element item instance parameter argument callback
context database file string number boolean array list map manager service
handler processor provider factory repository controller utility helper
component module system framework environment application connection client
server payload buffer index length count total price order product event message
error status type name path source destination temporary current previous next
first last start end create get set update delete remove add initialize validate
process handle calculate fetch load save send receive build make check ensure
return retrieve generate execute perform manage
""".split())

FORMAL_PHRASES = (
    "this function", "this method", "this module", "this class",
    "the purpose of", "it is important to", "please note", "note that",
    "ensures that", "ensure that", "facilitates", "utilizes", "utilises",
    "leverages", "comprehensive", "robust", "seamless", "efficient",
    "in order to", "as well as", "additionally", "furthermore", "moreover",
    "is responsible for", "designed to", "provides a", "allows you to",
    "used to", "the following", "in summary", "overall", "this allows",
    "this ensures", "this helps", "returns the", "args:", "returns:",
    "raises:", "yields:", "parameters:", "example usage", "examples:",
)

INFORMAL_RE = re.compile(
    r"\b(don't|dont|doesn't|doesnt|won't|wont|can't|cant|isn't|isnt|"
    r"it's|we'll|i'll|hack|fixme|todo|workaround|for now|legacy|magic|"
    r"temporary|ugly|mess|wtf|ugh)\b",
    re.IGNORECASE,
)

TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", re.IGNORECASE)
FORMAL_PHRASE_RE = re.compile("|".join(re.escape(p) for p in FORMAL_PHRASES), re.IGNORECASE)
BANNER_RE = re.compile(r"^(?:\s*[/*#=~_-]){8,}\s*$")
STEP_RE = re.compile(r"\b(step\s*\d+|first,|second,|third,|then,|finally,)\b", re.IGNORECASE)
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F1E6-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]"
)
API_DOC_RE = re.compile(r"(@param|@return|@throws|@brief|@brief|Args:|Returns:|Raises:)", re.IGNORECASE)
CODEISH_RE = re.compile(
    r"^\s*(?:if|for|while|switch|return|def|class|function|const|let|var|"
    r"import|from|print\s*\(|console\.|System\.|echo\s|\$|#include|"
    r"public\s|private\s|protected\s|try\b|catch\b|else\b|})"
)
DEBUG_PATTERNS = {
    "generic": (r"\bprint\s*\(", r"\bconsole\.log\s*\(", r"\bputs\s*\("),
}


@dataclass
class Comment:
    line: int
    text: str
    kind: str = "line"


@dataclass
class Finding:
    rule: str
    category: str
    weight: int
    message: str
    cap: int = 3
    fixable: bool = True
    risk: str = "low"
    count: int = 0
    lines: list[int] = field(default_factory=list)
    samples: list[str] = field(default_factory=list)

    def add(self, line: int | None = None, sample: object | None = None) -> None:
        self.count += 1
        if line is not None and len(self.lines) < 5 and line not in self.lines:
            self.lines.append(line)
        if sample is not None and len(self.samples) < 3:
            text = re.sub(r"\s+", " ", str(sample)).strip()[:180]
            if text and text not in self.samples:
                self.samples.append(text)

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "category": self.category,
            "weight": self.weight,
            "message": self.message,
            "cap": self.cap,
            "fixable": self.fixable,
            "risk": self.risk,
            "count": self.count,
            "lines": self.lines,
            "samples": self.samples,
        }


def mask_source(text: str, lang: str) -> tuple[str, list[Comment]]:
    """Blank strings and comments while preserving offsets and newlines."""
    masked = list(text)
    comments: list[Comment] = []
    n = len(text)
    i = 0
    line = 1
    hash_comments = lang in ("python", "php")
    slash_comments = lang in ("javascript", "php", "c", "cpp", "java", "generic")
    block_comments = slash_comments

    def blank(start: int, end: int) -> None:
        for k in range(start, end):
            if masked[k] not in "\r\n":
                masked[k] = " "

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            i += 1
            continue

        if lang == "php" and text.startswith("<<<", i):
            m = re.match(r"<<<\s*(['\"]?)([A-Za-z_]\w*)\1\s*\r?\n", text[i:])
            if m:
                ident = m.group(2)
                end_re = re.compile(r"(?m)^[ \t]*" + re.escape(ident) + r";?[ \t]*$")
                em = end_re.search(text, i + m.end())
                end = em.end() if em else n
                start_line = line
                line += text[i:end].count("\n")
                blank(i, end)
                i = end
                continue

        if lang == "python" and (text.startswith('"""', i) or text.startswith("'''", i)):
            quote = text[i:i + 3]
            end = text.find(quote, i + 3)
            end = n if end == -1 else end + 3
            _blank_string_prefix(masked, i, lang)
            line += text[i:end].count("\n")
            blank(i, end)
            i = end
            continue

        if lang == "java" and text.startswith('"""', i):
            end = text.find('"""', i + 3)
            end = n if end == -1 else end + 3
            line += text[i:end].count("\n")
            blank(i, end)
            i = end
            continue

        if lang == "cpp" and text.startswith('R"', i) and (
            i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")
        ):
            paren = text.find("(", i + 2)
            if paren != -1:
                delim = text[i + 2:paren]
                close = ")" + delim + '"'
                end = text.find(close, paren + 1)
                end = n if end == -1 else end + len(close)
                line += text[i:end].count("\n")
                blank(i, end)
                i = end
                continue

        if ch in ("'", '"', "`"):
            if ch == "`" and lang not in ("javascript", "php", "generic"):
                i += 1
                continue
            if lang == "python":
                _blank_string_prefix(masked, i, lang)
            end = i + 1
            while end < n:
                if text[end] == "\\":
                    end += 2
                    continue
                if text[end] == ch:
                    end += 1
                    break
                end += 1
            line += text[i:end].count("\n")
            blank(i, end)
            i = end
            continue

        if block_comments and text.startswith("/*", i):
            end = text.find("*/", i + 2)
            end = n if end == -1 else end + 2
            start_line = line
            chunk = text[i:end]
            comments.append(Comment(start_line, chunk, "block"))
            line += chunk.count("\n")
            blank(i, end)
            i = end
            continue

        if slash_comments and text.startswith("//", i):
            end = text.find("\n", i)
            end = n if end == -1 else end
            comments.append(Comment(line, text[i:end], "line"))
            blank(i, end)
            i = end
            continue

        if hash_comments and ch == "#":
            if lang == "php" and i + 1 < n and text[i + 1] == "[":
                i += 1
                continue
            end = text.find("\n", i)
            end = n if end == -1 else end
            comments.append(Comment(line, text[i:end], "line"))
            blank(i, end)
            i = end
            continue

        i += 1

    return "".join(masked), comments


def _blank_string_prefix(masked: list[str], index: int, lang: str) -> None:
    """Blank Python/C++ string prefixes such as f, r, b, u8."""
    k = index - 1
    limit = 2 if lang == "python" else 2
    while k >= 0 and index - k <= limit:
        ch = masked[k]
        if ch in "rbfuRBFUL8":
            masked[k] = " "
            k -= 1
        else:
            break


def split_identifier(name: str) -> list[str]:
    name = name.lstrip("$")
    parts = re.split(r"[_\W]+", name)
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|\d+", part))
    return [t.lower() for t in tokens if t]


def extract_identifiers(masked: str, lang: str) -> list[str]:
    names = re.findall(r"[A-Za-z_$][A-Za-z0-9_$]*", masked)
    result: list[str] = []
    for raw in names:
        name = raw.lstrip("$")
        if not name or name == "$" or name in KEYWORDS or name in BUILTINS:
            continue
        if name.lower() in NOISE_IDENTIFIERS:
            continue
        if name in STRING_PREFIXES:
            continue
        if name.startswith("__") and name.endswith("__"):
            continue
        if name.isupper():
            continue
        result.append(name)
    return result


def strip_comment_marker(text: str) -> str:
    s = text.strip()
    for prefix in ("///", "//!", "//", "/*!", "/**", "/*", "*/", "*", "#", "--"):
        if s.startswith(prefix):
            s = s[len(prefix):].strip()
            break
    return s.rstrip("*/").strip()


def looks_like_commented_code(text: str) -> bool:
    s = strip_comment_marker(text)
    if len(s) < 3 or len(s) > 160:
        return False
    if CODEISH_RE.search(s):
        return bool(re.search(r"[;{}=()]", s) or s.endswith((";", "{", "}")))
    return False


class FileAnalyzer:
    """Analyze one file and return a JSON-ready report."""

    def __init__(
        self,
        path: str,
        rel: str,
        text: str,
        lang: str,
        line_limit: int,
        has_formatter: bool = False,
    ) -> None:
        self.path = path
        self.rel = rel
        self.text = text
        self.lang = lang
        self.line_limit = line_limit
        self.has_formatter = has_formatter
        self.lines = text.splitlines()
        self.loc = sum(1 for line in self.lines if line.strip())
        self.masked, self.comments = mask_source(text, lang)
        self.findings: dict[str, Finding] = {}
        self.parse_error: str | None = None
        self.context: dict = {}
        self.identifiers: list[str] = []
        self.comment_lines: set[int] = set()

    def add(
        self,
        rule: str,
        category: str,
        weight: int,
        message: str,
        line: int | None = None,
        sample: object | None = None,
        cap: int = 3,
        fixable: bool = True,
        risk: str = "low",
    ) -> Finding:
        finding = self.findings.get(rule)
        if finding is None:
            finding = Finding(
                rule=rule, category=category, weight=weight, message=message,
                cap=cap, fixable=fixable, risk=risk,
            )
            self.findings[rule] = finding
        finding.add(line, sample)
        return finding

    def analyze(self) -> dict:
        self.analyze_formatting()
        from .languages import analyze_language
        analyze_language(self)
        self.analyze_comments()
        self.analyze_naming()
        self.analyze_structure()
        return self.finalize()

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def analyze_formatting(self) -> None:
        if not self.lines:
            return
        long_lines = [(i, line) for i, line in enumerate(self.lines, 1) if len(line) > self.line_limit]
        for line_no, line in long_lines[:6]:
            self.add(
                "FORMAT_LONG_LINE", "formatting", -1,
                f"Line exceeds {self.line_limit} characters",
                line_no, line.strip(), cap=2,
            )
        trailing = [i for i, line in enumerate(self.lines, 1) if line != line.rstrip()]
        for line_no in trailing[:6]:
            self.add(
                "FORMAT_TRAILING_WS", "formatting", -1,
                "Trailing whitespace", line_no, cap=1,
            )
        tab_lines = [i for i, line in enumerate(self.lines, 1) if line.startswith("\t")]
        if tab_lines:
            self.add(
                "FORMAT_TABS", "formatting", 0,
                "Tab indentation; neutral unless it conflicts with the project",
                tab_lines[0], cap=1,
            )
        space_indented = [line for line in self.lines if line.startswith("    ")]
        if len(tab_lines) >= 2 and len(space_indented) >= 2:
            self.add(
                "FORMAT_MIXED_INDENT", "formatting", -1,
                "Mixed tab and space indentation", None, cap=1,
            )
        if not self.text.endswith(("\n", "\r")):
            self.add(
                "FORMAT_NO_FINAL_NEWLINE", "formatting", -1,
                "Missing final newline", len(self.lines), cap=1,
            )
        if (
            self.loc >= 80
            and not self.has_formatter
            and not any(f.rule.startswith("FORMAT_") and f.weight < 0 for f in self.findings.values())
        ):
            self.add(
                "FORMAT_PERFECT", "formatting", 1,
                "No formatting drift; weak generated-style signal when combined with others",
                None, cap=1,
            )

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    def analyze_comments(self) -> None:
        for comment in self.comments:
            span = comment.text.count("\n") + 1
            for offset in range(span):
                self.comment_lines.add(comment.line + offset)

        all_text = "\n".join(c.text for c in self.comments)
        coverage = len(self.comment_lines) / max(self.loc, 1)
        if coverage > 0.35 and self.loc >= 40:
            self.add(
                "COMMENT_DOC_COVERAGE", "comments", 1,
                f"High comment coverage ({coverage:.0%} of non-blank lines)",
                None, cap=1,
            )

        formal = FORMAL_PHRASE_RE.findall(all_text)
        for phrase in formal[:6]:
            self.add(
                "COMMENT_FORMAL", "comments", 2,
                "Formal documentation filler",
                None, phrase, cap=2,
            )

        for comment in self.comments:
            for line in comment.text.splitlines():
                if BANNER_RE.match(line):
                    self.add(
                        "COMMENT_BANNER", "comments", 1,
                        "Decorative section banner",
                        comment.line, line.strip(), cap=1,
                    )
                    break

        for match in STEP_RE.finditer(all_text):
            self.add(
                "COMMENT_STEP", "comments", 1,
                "Step-by-step narration of trivial code",
                None, match.group(0), cap=1,
            )

        for comment in self.comments:
            if comment.kind != "line":
                continue
            body = strip_comment_marker(comment.text)
            if len(body) > 90 or INFORMAL_RE.search(body):
                continue
            next_line = ""
            for idx in range(comment.line, len(self.lines)):
                candidate = self.lines[idx].strip()
                if candidate:
                    next_line = candidate
                    break
            if next_line.startswith((
                "return", "pass", "break", "continue", "else", "}", "print(",
                "console.log", "i += ", "i++", "import ", "from ",
            )):
                self.add(
                    "COMMENT_TRIVIAL", "comments", 1,
                    "Comment restates an obvious statement",
                    comment.line, body, cap=2,
                )

        for match in EMOJI_RE.finditer(all_text):
            self.add(
                "COMMENT_EMOJI", "comments", 1,
                "Emoji in source comments", None, match.group(0), cap=1,
            )

        word_counts = [len(strip_comment_marker(c.text).split()) for c in self.comments]
        if len(word_counts) >= 3 and sum(word_counts) / len(word_counts) > 25:
            self.add(
                "COMMENT_LONG", "comments", 1,
                "Long average comment; may be over-documentation",
                None, cap=1,
            )

        for match in TODO_RE.finditer(all_text):
            self.add(
                "COMMENT_TODO", "comments", -2,
                "Real TODO/FIXME/HACK note",
                None, match.group(0), cap=2,
            )

        informal = INFORMAL_RE.findall(all_text)
        for word in informal[:4]:
            self.add(
                "COMMENT_INFORMAL", "comments", -1,
                "Informal or pragmatic comment tone",
                None, word, cap=1,
            )

        for comment in self.comments:
            if comment.kind == "line" and looks_like_commented_code(comment.text):
                self.add(
                    "COMMENTED_OUT_CODE", "comments", -1,
                    "Commented-out code left in place",
                    comment.line, strip_comment_marker(comment.text), cap=2,
                )

        if re.search(r"\b(for now|workaround|legacy|temporary|magic)\b", all_text, re.I):
            self.add(
                "COMMENT_DEBUG_NOTE", "comments", -1,
                "Ad-hoc debug or legacy note",
                None, cap=1,
            )

        api_docs = API_DOC_RE.findall(all_text)
        if api_docs:
            self.add(
                "COMMENT_API_DOC", "comments", 0,
                "API documentation is present; keep contracts and public docs",
                None, api_docs[0], cap=1, fixable=False,
            )

    # ------------------------------------------------------------------
    # Naming
    # ------------------------------------------------------------------

    def analyze_naming(self) -> None:
        self.identifiers = extract_identifiers(self.masked, self.lang)
        total = len(self.identifiers)
        if total == 0:
            return
        very_long = [x for x in self.identifiers if len(x) >= 28]
        long_ids = [x for x in self.identifiers if len(x) >= 18]
        short_ids = [x for x in self.identifiers if 2 <= len(x) <= 5]
        single = [x for x in self.identifiers if len(x) == 1]
        abbrev = [x for x in self.identifiers if x.lower() in ABBREV]
        enterprise = []
        verbose = []
        for name in self.identifiers:
            tokens = split_identifier(name)
            if any(t in ENTERPRISE_TOKENS for t in tokens):
                enterprise.append(name)
            if len(tokens) >= 4 and sum(1 for t in tokens if t in GENERIC_TOKENS) >= 2:
                verbose.append(name)

        for name in very_long[:3]:
            self.add(
                "NAME_VERY_LONG", "naming", 2,
                "Very long identifier", None, name, cap=2,
            )
        long_ratio = len(long_ids) / total
        if total >= 8 and long_ratio > 0.20:
            self.add(
                "NAME_LONG_RATIO", "naming", 2,
                f"{long_ratio:.0%} of identifiers are 18+ characters", None, cap=1,
            )
        avg_len = sum(len(x) for x in self.identifiers) / total
        if total >= 8 and avg_len >= 14:
            self.add(
                "NAME_AVG_LONG", "naming", 1,
                f"Average identifier length is {avg_len:.1f}", None, cap=1,
            )
        for name in enterprise[:2]:
            self.add(
                "NAME_ENTERPRISE", "naming", 2,
                "Enterprise-style name suffix or prefix", None, name, cap=2,
            )
        for name in verbose[:2]:
            self.add(
                "NAME_VERBOSE_COMPOUND", "naming", 1,
                "Verbose compound name built from generic words", None, name, cap=2,
            )
        if len(abbrev) >= 2 and len(abbrev) / total >= 0.02:
            self.add(
                "NAME_ABBREV", "naming", -1,
                "Uses conventional abbreviations", None,
                ", ".join(abbrev[:6]), cap=1,
            )
        if total >= 10 and len(short_ids) / total >= 0.18:
            self.add(
                "NAME_SHORT", "naming", -1,
                "Uses short local names", None,
                ", ".join(short_ids[:6]), cap=1,
            )
        if len(single) >= 2:
            self.add(
                "NAME_SINGLE_LETTER", "naming", -1,
                "Single-letter locals", None,
                ", ".join(sorted(set(single))[:6]), cap=1,
            )

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------

    def analyze_structure(self) -> None:
        function_count = int(self.context.get("function_count", 0))
        if self.lang == "python":
            depth = 0
            for line in self.lines:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                expanded = line.expandtabs(4)
                indent = len(expanded) - len(expanded.lstrip(" "))
                depth = max(depth, indent // 4)
        else:
            depth = 0
            current = 0
            for ch in self.masked:
                if ch == "{":
                    current += 1
                    depth = max(depth, current)
                elif ch == "}":
                    current = max(0, current - 1)
        if depth >= 5 and self.loc >= 30:
            self.add(
                "STRUCT_DEEP_NESTING", "structure", -1,
                f"Nesting depth reaches {depth}", None, cap=1,
            )

        for item in self.context.get("long_functions", [])[:3]:
            self.add(
                "STRUCT_LONG_FUNCTION", "structure", 0,
                "Long function; inspect for generated ceremony or real complexity",
                item.get("line"), item.get("name"), cap=3, fixable=False,
            )

        boilerplate = self._count_boilerplate()
        if boilerplate >= 2:
            self.add(
                "STRUCT_BOILERPLATE", "structure", 1,
                "Ceremonial project scaffold", None, cap=1,
            )

        abstraction = len(re.findall(
            r"\b(interface|abstract\s+class|implements|extends|factory|service|"
            r"repository|provider|strategy|adapter|facade|orchestrator|coordinator|"
            r"handler|processor|implementation|dto|dao)\b",
            self.masked, re.I,
        ))
        if abstraction >= 4:
            self.add(
                "STRUCT_EXCESSIVE_ABSTRACTION", "structure", 1,
                f"{abstraction} abstraction-related terms", None, cap=1,
            )

        defensive = len(re.findall(
            r"\b(try\b|catch\b|except\b|raise\b|isinstance\s*\(|"
            r"requireNonNull\s*\(|if\s+[^:\n]+is\s+None|if\s+not\s+\w+)",
            self.masked,
        ))
        if self.loc >= 30 and defensive * 100 / self.loc > 5:
            self.add(
                "STRUCT_DEFENSIVE", "structure", 1,
                "Heavy defensive boilerplate", None, cap=1,
            )

        if self.lang in DEBUG_PATTERNS:
            for rule in DEBUG_PATTERNS[self.lang]:
                for match in re.finditer(rule, self.masked):
                    line = self.masked.count("\n", 0, match.start()) + 1
                    self.add(
                        "STRUCT_DEBUG_LEFTOVER", "structure", -1,
                        "Debug output left in source", line, match.group(0), cap=2,
                    )

        if function_count and self.loc >= 40:
            self.context["function_count"] = function_count

    def _count_boilerplate(self) -> int:
        patterns = {
            "python": (
                r"if\s+__name__\s*==\s*['\"]__main__['\"]", r"\bargparse\b",
                r"\blogging\.getLogger\b", r"\bdataclass\b", r"from\s+__future__\s+import\s+annotations",
            ),
            "javascript": (
                r"['\"]use strict['\"]", r"require\.main\s*===\s*module",
                r"\bprocess\.argv\b", r"\bmodule\.exports\b", r"export\s+default",
            ),
            "php": (
                r"declare\s*\(\s*strict_types\s*=\s*1\s*\)", r"^\s*namespace\s+",
                r"vendor/autoload\.php", r"^\s*use\s+[\w\\]+;",
            ),
            "java": (
                r"public\s+static\s+void\s+main\s*\(", r"private\s+static\s+final\s+Logger",
                r"Objects\.requireNonNull\s*\(", r"@Override",
            ),
            "c": (r"#include\s*<stdio\.h>", r"int\s+main\s*\("),
            "cpp": (r"#include\s*<iostream>", r"int\s+main\s*\(", r"std::cout"),
            "generic": (),
        }
        return sum(
            len(re.findall(pattern, self.text, re.M))
            for pattern in patterns.get(self.lang, ())
        )

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def finalize(self) -> dict:
        scored = [f for f in self.findings.values() if f.weight != 0]
        ai_points = sum(f.weight * min(f.count, f.cap) for f in scored if f.weight > 0)
        human_points = sum(-f.weight * min(f.count, f.cap) for f in scored if f.weight < 0)
        ai_per_100 = ai_points * 100 / max(self.loc, 1)
        human_per_100 = human_points * 100 / max(self.loc, 1)
        raw = 50 + 6 * ai_per_100 - 5 * human_per_100
        size_factor = min(1.0, max(0.25, self.loc / 120))
        score = max(0.0, min(100.0, 50 + (raw - 50) * size_factor))
        if score >= 68:
            klass = "ai-shaped"
        elif score >= 45:
            klass = "mixed"
        else:
            klass = "human-shaped"
        categories = {f.category for f in scored}
        confidence = 0.30 + 0.20 * min(1.0, self.loc / 100) + 0.08 * len(categories)
        confidence = min(0.95, confidence)
        if 42 <= score <= 58:
            confidence *= 0.80
        if self.loc < 40:
            confidence *= 0.80
        findings = sorted(
            self.findings.values(),
            key=lambda f: (-abs(f.weight), f.rule),
        )
        return {
            "path": self.rel,
            "language": self.lang,
            "loc": self.loc,
            "score": round(score, 1),
            "class": klass,
            "confidence": round(confidence, 2),
            "ai_points": ai_points,
            "human_points": human_points,
            "line_limit": self.line_limit,
            "parse_error": self.parse_error,
            "findings": [f.to_dict() for f in findings],
        }
