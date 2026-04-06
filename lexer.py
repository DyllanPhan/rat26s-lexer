class Token:
    def __init__(self, type: str, lexeme: str, line: int = 0):
        self.type = type   
        self.lexeme = lexeme
        self.line = line

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
        self.line = 1

    def _peek(self, peek_pointer: int = 0):
        peek_position = self.position + peek_pointer
        return self.source_code_text[peek_position] if peek_position < self.source_length else "\0"

    def _advance(self):
        character = self._peek(0)
        if self.position < self.source_length:
            self.position += 1
            if character == "\n":
                self.line += 1
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
            return Token("eof", "", self.line)

        character = self._peek(0)

        if character in SEPARATORS:
            self._advance()
            return Token("separator", character, self.line)

        if character.isalpha():
            lex = self._scan_identifier_fsm()
            if lex.lower() in KEYWORDS:   
                return Token("keyword", lex, self.line)
            return Token("identifier", lex, self.line)

        if character.isdigit():
            token_type, lex = self._scan_number_fsm()
            return Token(token_type, lex, self.line)

        operator = self._scan_operator()
        if operator:
            return Token("operator", operator, self.line)

        self._advance()
        return Token("unknown", character, self.line)

class parser:
    def __init__(self, lexer, output_file, show_productions=True):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()
        self.show_productions = show_productions
        self.output_file = output_file
    def match(self, token):
        if self.current_token.lexeme == token or self.current_token.type == token:
            self.output_file.write(f"Token: {self.current_token.type: <15} Lexeme: {self.current_token.lexeme}\n")
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Expected {token} but got {self.current_token.type} {self.current_token.lexeme}")
        
    def first_opt_function_definitions(self):
        return self.current_token.lexeme == "function"
    
    def first_opt_parameter_list(self):
        return self.current_token.type == "identifier"

    def first_qualifier(self):
        return self.current_token.lexeme in {"integer", "boolean", "real"}
    
    def first_statement_list(self):
        return self.current_token.lexeme in {"{", "if", "return", "write", "read", "while"} or self.current_token.type == "identifier"

    def first_relop(self):
        return self.current_token.lexeme in {"==", "!=", ">", "<", "<=", "=>"}

    def Rat26s(self):
        self.match('@')
        if self.show_productions:
            self.output_file.write("R1. <Rat26S> ::= @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @\n")
        self.opt_function_definitions()
        self.match('@')
        self.opt_declaration_list()
        self.match('@')
        self.statement_list()
        self.match('@')
        
    def opt_function_definitions(self):
        if self.first_opt_function_definitions():
            if self.show_productions:
                self.output_file.write("R2. <Opt Function Definitions> ::= <Function Definitions>\n")
            self.function_definitions()
        else:
            if self.show_productions:
                self.output_file.write("R3. <Opt Function Definitions> ::= <Empty>\n")
            self.empty()
    
    def function_definitions(self):
        self.function()
        if self.first_opt_function_definitions():
            if self.show_productions:
                self.output_file.write("R4. <Function Definitions> ::= <Function> <Function Definitions>\n")
            self.function_definitions()
        else:
            if self.show_productions:
                self.output_file.write("R5. <Function Definitions> ::= <Function>\n")
        
    def function(self):
        self.match("function")
        if self.show_productions:
            self.output_file.write("R6. <Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>\n")
        self.match("identifier")
        self.match('(')
        self.opt_parameter_list()
        self.match(')')
        self.opt_declaration_list()
        self.body()
        
    def opt_parameter_list(self):
        if self.first_opt_parameter_list():
            if self.show_productions:
                self.output_file.write("R7. <Opt parameter List> ::= <Parameter List>\n")
            self.parameter_list()
        else:
            if self.show_productions:
                self.output_file.write("R8. <Opt parameter List> ::= <Empty>\n")
            self.empty()
            
    def parameter_list(self):
        self.parameter()
        if self.current_token.lexeme == ',':
            if self.show_productions:
                self.output_file.write("R9. <Parameter List> ::= <Parameter> , <Parameter List>\n")
            self.match(',')
            self.parameter_list() 
        else:
            if self.show_productions:
                self.output_file.write("R10. <Parameter List> ::= <Parameter>\n")

    def parameter(self):
        if self.show_productions:
            self.output_file.write("R11. <Parameter> ::= <IDS> <Qualifier>\n")
        self.ids()
        self.qualifier()
    
    def qualifier(self):
        if self.show_productions:
            self.output_file.write("R12. <Qualifier> ::= integer | boolean | real\n")
        if self.first_qualifier():
            self.match(self.current_token.lexeme)
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Expected a type but got {self.current_token.type} {self.current_token.lexeme}")
        
    def body(self):
        self.match('{')
        if self.show_productions:
            self.output_file.write("R13. <Body> ::= { <Statement List> }\n")
        self.statement_list()
        self.match('}')
    
    def opt_declaration_list(self):
        if self.first_qualifier():
            if self.show_productions:
                self.output_file.write("R14. <Opt Declaration List> ::= <Declaration List>\n")
            self.declaration_list()
        else:
            if self.show_productions:
                self.output_file.write("R15. <Opt Declaration List> ::= <Empty>\n")
            self.empty()
        
    def declaration_list(self):
        self.declaration()
        if self.first_qualifier():
            if self.show_productions:
                self.output_file.write("R16. <Declaration List> ::= <Declaration> ; <Declaration List>\n")
            self.match(';')
            self.declaration_list()
        else:
            if self.show_productions:
                self.output_file.write("R17. <Declaration List> ::= <Declaration> ;\n")
            self.match(';')
        
    def declaration(self):
        self.qualifier()
        if self.show_productions:
            self.output_file.write("R18. <Declaration> ::= <Qualifier> <IDS>\n")
        self.ids()
        
    def ids(self):
        self.match("identifier")
        if self.current_token.lexeme ==',':
            if self.show_productions:
                self.output_file.write("R19. <IDS> ::= <Identifier> , <IDS>\n")
            self.match(',')
            self.ids()
        else:
            if self.show_productions:
                self.output_file.write("R20. <IDS> ::= <Identifier>\n")
    
    def statement_list(self):
        self.statement()
        if self.first_statement_list():
            if self.show_productions:
                self.output_file.write("R21. <Statement List> ::= <Statement> <Statement List>\n")
            self.statement_list()
        else:
            if self.show_productions:
                self.output_file.write("R22. <Statement List> ::= <Statement>\n")
            
    def statement(self):
        if self.show_productions:
            self.output_file.write("R23. <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>\n")
        if self.current_token.lexeme == '{':
            self.compound()
        elif self.current_token.type == "identifier":
            self.assign()
        elif self.current_token.lexeme == "if":
            self.if_production()
        elif self.current_token.lexeme == "return":
            self.return_production()
        elif self.current_token.lexeme == "write":
            self.print_production()
        elif self.current_token.lexeme == "read":
            self.scan_production()
        elif self.current_token.lexeme == "while":
            self.while_production()
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Unexpected token {self.current_token.type} {self.current_token.lexeme}")

    def compound(self):
        self.match('{')
        if self.show_productions:
            self.output_file.write("R24. <Compound> ::= { <Statement List> }\n")
        self.statement_list()
        self.match('}')
    
    def assign(self):
        self.match("identifier")
        if self.show_productions:
            self.output_file.write("R25. <Assign> ::= <Identifier> = <Expression> ;\n")
        self.match('=')
        self.expression()
        self.match(';')

    def if_production(self):
        self.match("if")
        self.match('(')
        self.condition()
        self.match(')')
        self.statement()
        if self.current_token.lexeme == "otherwise":
            self.match("otherwise")
            self.statement()
        self.match("fi")

    def return_production(self):
        self.match("return")
        if self.current_token.lexeme == ";":
            if self.show_productions:
                self.output_file.write("R28. <Return> ::= return ;\n")
            self.match(';')
        else:
            if self.show_productions:
                self.output_file.write("R29. <Return> ::= return <Expression> ;\n")
            self.expression()
            self.match(';')

    def print_production(self):
        if self.show_productions:
            self.output_file.write("R20. <Print> ::= write ( <Expression> ) ;\n")
        self.match("write")
        self.match('(')
        self.expression()
        self.match(')')
        self.match(';')

    def scan_production(self):
        self.match("read")
        if self.show_productions:
            self.output_file.write("R31. <Scan> ::= read ( <IDS> ) ;\n")
        self.match('(')
        self.ids()
        self.match(')')
        self.match(';')
        
    def while_production(self):
        self.match("while")
        if self.show_productions:
            self.output_file.write("R32. <While> ::= while ( <Condition> ) <Statement>\n")
        self.match('(')
        self.condition()
        self.match(')')
        self.statement()
        
    def condition(self):
        self.expression()
        if self.show_productions:
            self.output_file.write("R33. <Condition> ::= <Expression> <Relop> <Expression>\n")
        self.relop()
        self.expression()
        
    def relop(self):
        if self.show_productions:
            self.output_file.write("R34. <Relop> ::= == | != | > | < | <= | >=\n")
        if self.first_relop():
            self.match(self.current_token.lexeme)
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Expected a relational operator but got {self.current_token.type} {self.current_token.lexeme}")

    def expression(self):
        self.term()
        self.expression_prime()
        if self.show_productions:
            self.output_file.write("R35. <Expression> ::= <Term> <Expression'>\n")
        
        
    def expression_prime(self):
        if self.current_token.lexeme == '+':
            if self.show_productions:
                self.output_file.write("R36. <Expression'> ::= + <Term> <Expression'>\n")
            self.match('+')
            self.term()
            self.expression_prime()
        elif self.current_token.lexeme == '-':
            if self.show_productions:
                self.output_file.write("R37. <Expression'> ::= - <Term> <Expression'>\n")
            self.match('-')
            self.term()
            self.expression_prime()
        else:
            if self.show_productions:
                self.output_file.write("R38. <Expression'> ::= <Empty>\n")
            self.empty()
        
    def term(self):
        self.factor()
        self.term_prime()
        if self.show_productions:
            self.output_file.write("R39. <Term> ::= <Factor> <Term'>\n")
        
        
    def term_prime(self):
        if self.current_token.lexeme == '*':
            if self.show_productions:
                self.output_file.write("R40. <Term'> ::= * <Factor> <Term'>\n")
            self.match('*')
            self.factor()
            self.term_prime()
        elif self.current_token.lexeme == '/':
            if self.show_productions:
                self.output_file.write("R41. <Term'> ::= / <Factor> <Term'>\n")
            self.match('/')
            self.factor()
            self.term_prime()
        else:
            if self.show_productions:
                self.output_file.write("R42. <Term'> ::= <Empty>\n")
            self.empty()
        
    def factor(self):
        if self.current_token.lexeme == '-':
            self.match('-')
            self.primary()
            if self.show_productions:
                self.output_file.write("R43. <Factor> ::= - <Primary>\n")
        else:
            self.primary()
            if self.show_productions:
                self.output_file.write("R44. <Factor> ::= <Primary>\n")
            
        
    def primary(self):
        if self.current_token.type == "identifier":
            self.match("identifier")
            if self.show_productions:
                self.output_file.write("R45. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDS> ) | ( <Expression> ) | <Real> | true | false\n")
            if self.current_token.lexeme == '(':
                self.match('(')
                self.ids()
                self.match(')')
        elif self.current_token.type in {"integer", "real"}:
            self.match(self.current_token.type)
            if self.show_productions:
                self.output_file.write("R45. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDS> ) | ( <Expression> ) | <Real> | true | false\n")
        elif self.current_token.lexeme in {"true", "false"}:
            self.match(self.current_token.lexeme)
            if self.show_productions:
                self.output_file.write("R45. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDS> ) | ( <Expression> ) | <Real> | true | false\n")
        elif self.current_token.lexeme == '(':
            self.match('(')
            if self.show_productions:
                self.output_file.write("R45. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDS> ) | ( <Expression> ) | <Real> | true | false\n")
            self.expression()
            self.match(')')
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Unexpected token {self.current_token.type} {self.current_token.lexeme} in primary")
    def empty(self):
        if self.show_productions:
            self.output_file.write("R46. <Empty> ::= ε\n")
        pass

inputFile = input("Please enter the input Rat26S source code file: ")
outputFile = input("Please enter the output destination: ")

with open(outputFile, "w") as output:
    parse = parser(Lexer(open(inputFile, "r").read()), output, show_productions=True)
    parse.Rat26s()
print("Done.")