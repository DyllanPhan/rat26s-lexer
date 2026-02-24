from dataclasses import dataclass
from typing import Optional, TextIO

@dataclass
class Token:
    type: str   
    lexeme: str

KEYWORDS = {
    "integer", "boolean", "real",
    "function", "if", "otherwise", "fi",
    "while", "return", "read", "write",
    "true", "false",
}

SEPARATORS = {"(", ")", "{", "}", ",", ";", "@"}
OPERATORS = {"==", "!=", "<=", "=>", ">", "<", "=", "+", "-", "*", "/"}
WHITESPACE = {" ", "\t", "\n", "\r"}

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)

    def _peek(self, k: int = 0) -> str:
        j = self.i + k
        return self.text[j] if j < self.n else "\0"

    def _advance(self) -> str:
        ch = self._peek(0)
        if self.i < self.n:
            self.i += 1
        return ch

    def _at_end(self) -> bool:
        return self.i >= self.n

    def _skip_ignored(self):
        while True:
            while self._peek(0) in WHITESPACE:
                self._advance()
            if self._peek(0) == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while not self._at_end():
                    if self._peek(0) == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                continue

            break


    def _scan_identifier_fsm(self) -> str:
        start = self.i

        ch = self._peek(0)
        if not ch.isalpha():
            return ""

        self._advance()  

        while True:
            ch = self._peek(0)
            if ch.isalpha() or ch.isdigit() or ch == "_":
                self._advance()
            else:
                break

        return self.text[start:self.i]

    def _scan_number_fsm(self) -> tuple[str, str]:
        start = self.i

        if not self._peek(0).isdigit():
            return ("", "")
        while self._peek(0).isdigit():
            self._advance()

        if self._peek(0) == "." and self._peek(1).isdigit():
            self._advance()
            while self._peek(0).isdigit():
                self._advance()
            return ("real", self.text[start:self.i])

        return ("integer", self.text[start:self.i])

    def _scan_operator(self) -> str:
        two = self._peek(0) + self._peek(1)
        if two in OPERATORS:
            self._advance()
            self._advance()
            return two
        one = self._peek(0)
        if one in OPERATORS:
            self._advance()
            return one
        return ""

    def next_token(self) -> Token:
        self._skip_ignored()

        if self._at_end():
            return Token("eof", "")

        ch = self._peek(0)

        if ch in SEPARATORS:
            self._advance()
            return Token("separator", ch)

        if ch.isalpha():
            lex = self._scan_identifier_fsm()
            if lex.lower() in KEYWORDS:   
                return Token("keyword", lex)
            return Token("identifier", lex)

        if ch.isdigit():
            ttype, lex = self._scan_number_fsm()
            return Token(ttype, lex)

        op = self._scan_operator()
        if op:
            return Token("operator", op)

        self._advance()
        return Token("unknown", ch)


def run_lexer(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = Lexer(text)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"{'token':<15} {'lexeme'}\n")
        out.write(f"{'-'*15} {'-'*20}\n")

        while True:
            tok = lexer.next_token()
            if tok.type == "eof":
                break
            out.write(f"{tok.type:<15} {tok.lexeme}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python lexer.py <input_file> <output_file>")
        sys.exit(1)

    run_lexer(sys.argv[1], sys.argv[2])
    print("Done.")