class Token:
    def __init__(self, type: str, lexeme: str):
        self.type = type   
        self.lexeme = lexeme

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
        self.source_code_text = text
        self.position = 0
        self.source_length = len(text)

    def _peek(self, peek_pointer: int = 0):
        peek_position = self.position + peek_pointer
        return self.source_code_text[peek_position] if peek_position < self.source_length else "\0"

    def _advance(self):
        character = self._peek(0)
        if self.position < self.source_length:
            self.position += 1
        return character

    def _at_end(self):
        return self.position >= self.source_length

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


    def _scan_identifier_fsm(self):
        start = self.position

        character = self._peek(0)
        if not character.isalpha():
            return ""

        self._advance()  

        while True:
            character = self._peek(0)
            if character.isalpha() or character.isdigit() or character == "_":
                self._advance()
            else:
                break

        return self.source_code_text[start:self.position]

    def _scan_number_fsm(self):
        start = self.position

        if not self._peek(0).isdigit():
            return ("", "")
        while self._peek(0).isdigit():
            self._advance()

        if self._peek(0) == "." and self._peek(1).isdigit():
            self._advance()
            while self._peek(0).isdigit():
                self._advance()
            return ("real", self.source_code_text[start:self.position])

        return ("integer", self.source_code_text[start:self.position])

    def _scan_operator(self):
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

    def next_token(self):
        self._skip_ignored()

        if self._at_end():
            return Token("eof", "")

        character = self._peek(0)

        if character in SEPARATORS:
            self._advance()
            return Token("separator", character)

        if character.isalpha():
            lex = self._scan_identifier_fsm()
            if lex.lower() in KEYWORDS:   
                return Token("keyword", lex)
            return Token("identifier", lex)

        if character.isdigit():
            token_type, lex = self._scan_number_fsm()
            return Token(token_type, lex)

        operator = self._scan_operator()
        if operator:
            return Token("operator", operator)

        self._advance()
        return Token("unknown", character)


def run_lexer(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = Lexer(text)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"{'token':<15} {'lexeme'}\n")
        out.write(f"{'-'*15} {'-'*20}\n")

        while True:
            token = lexer.next_token()
            if token.type == "eof":
                break
            out.write(f"{token.type:<15} {token.lexeme}\n")

inputFile = input("Please enter the input Rat26S source code file: ")
outputFile = input("Please enter the output destination: ")

run_lexer(inputFile, outputFile)
print("Done.")