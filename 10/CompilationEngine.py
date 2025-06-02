from JackTokenizer import JackTokenizer

# Jack operators
OPS       = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OPS = {"-", "~"}


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer, output_stream) -> None:
        self.tk   = tokenizer
        self.out  = output_stream
        self.ind  = 0
        if self.tk.has_more_tokens():
            self.tk.advance()

    def _w(self, text: str = "") -> None:
        self.out.write("  " * self.ind + text + "\n")

    def _esc(self, s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _write_token(self) -> None:
        ttype = self.tk.token_type()
        raw   = self.tk.current_token()

        if ttype == "INT_CONST":
            tag = "integerConstant"
        elif ttype == "STRING_CONST":
            tag = "stringConstant"
            raw = raw[1:-1]            # drop quotes
        else:
            tag = ttype.lower()

        txt = self._esc(raw)
        self._w(f"<{tag}> {txt} </{tag}>")
        if self.tk.has_more_tokens():
            self.tk.advance()

    def _expect(self, lexeme: str) -> None:
        assert self.tk.current_token() == lexeme, f"Expected '{lexeme}'"
        self._write_token()

    def compile_class(self) -> None:
        self._w("<class>")
        self.ind += 1
        self._expect("class")
        self._write_token()                    # className
        self._expect("{")

        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"static", "field"}:
            self.compile_class_var_dec()
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"constructor", "function", "method"}:
            self.compile_subroutine_dec()

        self._expect("}")
        self.ind -= 1
        self._w("</class>")

    def compile_class_var_dec(self) -> None:
        self._w("<classVarDec>")
        self.ind += 1
        self._write_token()          # static|field
        self._write_token()          # type
        self._write_token()          # varName
        while self.tk.current_token() == ",":
            self._write_token()
            self._write_token()
        self._expect(";")
        self.ind -= 1
        self._w("</classVarDec>")

    def compile_subroutine_dec(self) -> None:
        self._w("<subroutineDec>")
        self.ind += 1
        self._write_token()          # constructor|function|method
        self._write_token()          # returnType
        self._write_token()          # subroutineName
        self._expect("(")
        self.compile_parameter_list()
        self._expect(")")
        self.compile_subroutine_body()
        self.ind -= 1
        self._w("</subroutineDec>")

    def compile_parameter_list(self) -> None:
        self._w("<parameterList>")
        self.ind += 1
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ")"):
            self._write_token()
            self._write_token()
            while self.tk.current_token() == ",":
                self._write_token()
                self._write_token()
                self._write_token()
        self.ind -= 1
        self._w("</parameterList>")

    def compile_subroutine_body(self) -> None:
        self._w("<subroutineBody>")
        self.ind += 1
        self._expect("{")
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self._expect("}")
        self.ind -= 1
        self._w("</subroutineBody>")

    def compile_var_dec(self) -> None:
        self._w("<varDec>")
        self.ind += 1
        self._write_token()          # 'var'
        self._write_token()          # type
        self._write_token()          # varName
        while self.tk.current_token() == ",":
            self._write_token()
            self._write_token()
        self._expect(";")
        self.ind -= 1
        self._w("</varDec>")

    def compile_statements(self) -> None:
        self._w("<statements>")
        self.ind += 1
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"let", "if", "while", "do", "return"}:
            kw = self.tk.keyword()
            if   kw == "let":    self.compile_let()
            elif kw == "if":     self.compile_if()
            elif kw == "while":  self.compile_while()
            elif kw == "do":     self.compile_do()
            elif kw == "return": self.compile_return()
        self.ind -= 1
        self._w("</statements>")

    def compile_let(self) -> None:
        self._w("<letStatement>")
        self.ind += 1
        self._write_token()              # 'let'
        self._write_token()              # varName
        if self.tk.current_token() == "[":
            self._write_token()
            self.compile_expression()
            self._expect("]")
        self._expect("=")
        self.compile_expression()
        self._expect(";")
        self.ind -= 1
        self._w("</letStatement>")

    def compile_if(self) -> None:
        self._w("<ifStatement>")
        self.ind += 1
        self._write_token()
        self._expect("(")
        self.compile_expression()
        self._expect(")")
        self._expect("{")
        self.compile_statements()
        self._expect("}")
        if self.tk.token_type() == "KEYWORD" and self.tk.keyword() == "else":
            self._write_token()
            self._expect("{")
            self.compile_statements()
            self._expect("}")
        self.ind -= 1
        self._w("</ifStatement>")

    def compile_while(self) -> None:
        self._w("<whileStatement>")
        self.ind += 1
        self._write_token()
        self._expect("(")
        self.compile_expression()
        self._expect(")")
        self._expect("{")
        self.compile_statements()
        self._expect("}")
        self.ind -= 1
        self._w("</whileStatement>")

    def compile_do(self) -> None:
        self._w("<doStatement>")
        self.ind += 1
        self._write_token()
        self.compile_subroutine_call()
        self._expect(";")
        self.ind -= 1
        self._w("</doStatement>")

    def compile_return(self) -> None:
        self._w("<returnStatement>")
        self.ind += 1
        self._write_token()
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ";"):
            self.compile_expression()
        self._expect(";")
        self.ind -= 1
        self._w("</returnStatement>")

    def compile_expression(self) -> None:
        self._w("<expression>")
        self.ind += 1
        self.compile_term()
        while self.tk.token_type() == "SYMBOL" and self.tk.current_token() in OPS:
            self._write_token()
            self.compile_term()
        self.ind -= 1
        self._w("</expression>")

    def compile_term(self) -> None:
        self._w("<term>")
        self.ind += 1
        ttype = self.tk.token_type()
        token = self.tk.current_token()

        if ttype in {"INT_CONST", "STRING_CONST"}:
            self._write_token()
        elif ttype == "KEYWORD" and token in {"true", "false", "null", "this"}:
            self._write_token()
        elif ttype == "IDENTIFIER":
            nxt = (self.tk.tokens[self.tk.current_token_index + 1]
                   if self.tk.current_token_index + 1 < len(self.tk.tokens) else None)

            if nxt == "[":
                self._write_token()
                self._expect("[")
                self.compile_expression()
                self._expect("]")
            elif nxt in {"(", "."}:
                self.compile_subroutine_call()  # consumes ')' as well
            else:
                self._write_token()
        elif ttype == "SYMBOL" and token == "(":
            self._write_token()
            self.compile_expression()
            self._expect(")")
        elif ttype == "SYMBOL" and token in UNARY_OPS:
            self._write_token()
            self.compile_term()
        else:
            raise ValueError(f"Bad term starting with '{token}'")

        self.ind -= 1
        self._w("</term>")

    def compile_subroutine_call(self) -> None:
        self._write_token()                    # identifier or className/varName
        if self.tk.current_token() == ".":
            self._write_token()                # '.'
            self._write_token()                # subroutineName
        self._expect("(")
        self.compile_expression_list()
        self._expect(")")

    def compile_expression_list(self) -> None:
        self._w("<expressionList>")
        self.ind += 1
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ")"):
            self.compile_expression()
            while self.tk.current_token() == ",":
                self._write_token()
                self.compile_expression()
        self.ind -= 1
        self._w("</expressionList>")