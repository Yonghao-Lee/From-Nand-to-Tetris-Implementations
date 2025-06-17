import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    KEYWORDS = {
        "class", "constructor", "function", "method", "field", "static", "var",
        "int", "char", "boolean", "void", "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return"
    }
    SYMBOLS = "{}()[].,;+-*/&|<>=~"         

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it."""
        self.keywords = JackTokenizer.KEYWORDS
        self.symbols  = set(JackTokenizer.SYMBOLS)

        content = input_stream.read()
        content = self._remove_comments(content)

        self.tokens: list[str] = self._tokenize(content)
        self.current_token_index = -1
        self._cur_tok: str | None = None          

    def has_more_tokens(self) -> bool:
        return self.current_token_index < len(self.tokens) - 1

    def advance(self) -> None:
        if self.has_more_tokens():
            self.current_token_index += 1
            self._cur_tok = self.tokens[self.current_token_index]

    def current_token(self) -> str | None:
        return self._cur_tok

    def token_type(self) -> str | None:
        if self._cur_tok is None:
            return None
        if self._cur_tok in self.keywords:
            return "KEYWORD"
        if self._cur_tok in self.symbols:
            return "SYMBOL"
        if self._cur_tok.startswith('"') and self._cur_tok.endswith('"'):
            return "STRING_CONST"
        if self._cur_tok.isdigit():
            return "INT_CONST"          
        return "IDENTIFIER"

    def keyword(self) -> str:
        if self.token_type() == "KEYWORD":
            return self._cur_tok.lower()
        raise ValueError("Current token is not a keyword")

    def symbol(self) -> str:
        return self._cur_tok

    def identifier(self) -> str:
        return self._cur_tok

    def int_val(self) -> int:
        return int(self._cur_tok)

    def string_val(self) -> str:
        return self._cur_tok[1:-1]

    def _remove_comments(self, content: str) -> str:
        """Strip comments but leave anything inside string constants intact."""
        result = []
        i = 0
        in_string = False

        while i < len(content):
            ch = content[i]

            # toggle literal mode
            if ch == '"' and not in_string:
                in_string = True
                result.append(ch)
                i += 1
                continue
            elif ch == '"' and in_string:
                in_string = False
                result.append(ch)
                i += 1
                continue

            if not in_string:
                # single-line //
                if i < len(content) - 1 and content[i:i + 2] == "//":
                    while i < len(content) and content[i] != "\n":
                        i += 1
                    continue
                # block /* … */
                if i < len(content) - 1 and content[i:i + 2] == "/*":
                    i += 2
                    while i < len(content) - 1:
                        if content[i:i + 2] == "*/":
                            i += 2
                            break
                        i += 1
                    continue

            # ordinary character
            result.append(ch)
            i += 1

        return "".join(result)

    def _tokenize(self, content: str) -> list[str]:
        tokens = []
        i = 0
        while i < len(content):
            c = content[i]
            if c.isspace():
                i += 1
                continue
            if c in self.symbols:
                tokens.append(c)
                i += 1
                continue
            if c == '"':
                s = '"'
                i += 1
                while i < len(content) and content[i] not in '"\n':
                    s += content[i]
                    i += 1
                if i < len(content) and content[i] == '"':
                    s += '"'
                    i += 1
                tokens.append(s)
                continue
            if c.isalnum() or c == "_":
                t = ""
                while i < len(content) and (content[i].isalnum() or content[i] == "_"):
                    t += content[i]
                    i += 1
                tokens.append(t)
                continue
            # unrecognized char: skip
            i += 1
        return tokens 