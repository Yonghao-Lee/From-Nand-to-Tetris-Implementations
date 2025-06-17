from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

OPS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OPS = {"-", "~"}


class CompilationEngine:
    """Compiles Jack code to VM code using recursive descent parsing."""
    
    def __init__(self, tokenizer: JackTokenizer, vm_writer: VMWriter) -> None:
        self.tk = tokenizer
        self.vm_writer = vm_writer
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.label_counter = 0

        if self.tk.has_more_tokens():
            self.tk.advance()
            
    def _advance(self) -> None:
        """Advance to next token."""
        if self.tk.has_more_tokens():
            self.tk.advance()

    def _expect(self, lexeme: str) -> None:
        """Expect specific token and advance."""
        assert self.tk.current_token() == lexeme, f"Expected '{lexeme}'"
        self._advance()

    def compile_class(self) -> None:
        """Compile complete class declaration."""
        self._expect("class")
        self.class_name = self.tk.current_token()
        self._advance()
        self._expect("{")
        
        # Compile class variables
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"static", "field"}:
            self.compile_class_var_dec()
        
        # Compile subroutines
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"constructor", "function", "method"}:
            self.compile_subroutine_dec()
        
        self._expect("}")

    def compile_class_var_dec(self) -> None:
        """Compile class variable declaration."""
        kind = self.tk.current_token().upper()
        self._advance()
        var_type = self.tk.current_token()
        self._advance()

        # First variable
        var_name = self.tk.current_token()
        self.symbol_table.define(var_name, var_type, kind)
        self._advance()

        # Additional variables
        while self.tk.current_token() == ",":
            self._advance()
            var_name = self.tk.current_token()
            self.symbol_table.define(var_name, var_type, kind)
            self._advance()
        
        self._expect(";")

    def compile_subroutine_dec(self) -> None:
        """Compile subroutine declaration and generate VM function."""
        self.symbol_table.start_subroutine()
        subroutine_type = self.tk.current_token()
        self._advance()
        return_type = self.tk.current_token()
        self._advance()
        subroutine_name = self.tk.current_token()
        self._advance()
        
        # Methods get implicit 'this' parameter
        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "ARG")
        
        self._expect('(')
        self.compile_parameter_list()
        self._expect(')')
        self._expect('{')

        # Count local variables
        var_count = 0
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() == "var":
            var_count += self.compile_var_dec()
        
        # Generate VM function declaration
        self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}", var_count)

        # Setup object pointer for constructors/methods
        if subroutine_type == "constructor":
            num_fields = self.symbol_table.var_count("FIELD")
            self.vm_writer.write_push("CONSTANT", num_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif subroutine_type == "method":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
        
        self.compile_statements()
        self._expect('}')

    def compile_parameter_list(self) -> None:
        """Compile parameter list for subroutine."""
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ")"):
            # First parameter
            param_type = self.tk.current_token()
            self._advance()
            param_name = self.tk.current_token()
            self.symbol_table.define(param_name, param_type, "ARG")
            self._advance()
            
            # Additional parameters
            while self.tk.current_token() == ",":
                self._advance()
                param_type = self.tk.current_token()
                self._advance()
                param_name = self.tk.current_token()
                self.symbol_table.define(param_name, param_type, "ARG")
                self._advance()

    def compile_subroutine_body(self) -> None:
        """Compile subroutine body."""
        self._expect("{")
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self._expect("}")

    def compile_var_dec(self) -> int:
        """Compile local variable declaration. Returns count of variables declared."""
        self._expect("var")
        var_type = self.tk.current_token()
        self._advance()
        
        count = 0
        # First variable
        var_name = self.tk.current_token()
        self.symbol_table.define(var_name, var_type, "VAR")
        self._advance()
        count += 1
        
        # Additional variables
        while self.tk.current_token() == ",":
            self._advance()
            var_name = self.tk.current_token()
            self.symbol_table.define(var_name, var_type, "VAR")
            self._advance()
            count += 1
        
        self._expect(";")
        return count

    def compile_statements(self) -> None:
        """Compile sequence of statements."""
        while self.tk.token_type() == "KEYWORD" and self.tk.keyword() in {"let", "if", "while", "do", "return"}:
            kw = self.tk.keyword()
            if   kw == "let":    self.compile_let()
            elif kw == "if":     self.compile_if()
            elif kw == "while":  self.compile_while()
            elif kw == "do":     self.compile_do()
            elif kw == "return": self.compile_return()

    def compile_let(self) -> None:
        """Compile let statement with array support."""
        self._expect("let")
        var_name = self.tk.current_token()
        self._advance()

        is_array = False
        if self.tk.current_token() == "[":
            is_array = True
            # Push array base address
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            segment = self._kind_to_segment(kind)
            self.vm_writer.write_push(segment, index) 

            self._advance()
            self.compile_expression()  # Array index
            self._expect("]")
            self.vm_writer.write_arithmetic("ADD")
        
        self._expect("=")
        self.compile_expression()  # Value to assign

        if is_array:
            # Store to array element using THAT pointer
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            # Store to simple variable
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            segment = self._kind_to_segment(kind)
            self.vm_writer.write_pop(segment, index)
        
        self._expect(";")

    def compile_if(self) -> None:
        """Compile if statement with optional else."""
        self._expect("if")
        self._expect("(")
        self.compile_expression()
        self._expect(")")

        # Generate unique labels
        else_label = f"IF_ELSE_{self.label_counter}"
        end_label = f"IF_END_{self.label_counter}"
        self.label_counter += 1

        # Jump to else if condition is false
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(else_label)

        self._expect("{")
        self.compile_statements()
        self._expect("}")

        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(else_label)

        # Optional else clause
        if self.tk.token_type() == "KEYWORD" and self.tk.keyword() == "else":
            self._expect("else")
            self._expect("{")
            self.compile_statements()
            self._expect("}")
        
        self.vm_writer.write_label(end_label)

    def compile_while(self) -> None:
        """Compile while loop."""
        loop_label = f"WHILE_LOOP_{self.label_counter}"
        end_label = f"WHILE_END_{self.label_counter}"
        self.label_counter += 1

        self.vm_writer.write_label(loop_label)

        self._expect("while")
        self._expect("(")
        self.compile_expression()
        self._expect(")")

        # Exit loop if condition is false
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(end_label)

        self._expect("{")
        self.compile_statements()
        self._expect("}")

        self.vm_writer.write_goto(loop_label)
        self.vm_writer.write_label(end_label)

    def compile_do(self) -> None:
        """Compile do statement and discard return value."""
        self._expect("do")
        self.compile_subroutine_call()
        self.vm_writer.write_pop("TEMP", 0)  # Discard return value
        self._expect(";")

    def compile_return(self) -> None:
        """Compile return statement."""
        self._expect("return")
        
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ";"):
            self.compile_expression()  # Return value
        else:
            self.vm_writer.write_push("CONSTANT", 0)  # Void return

        self._expect(";")
        self.vm_writer.write_return()

    def compile_expression(self) -> None:
        """Compile expression with binary operators."""
        self.compile_term()
        
        while self.tk.token_type() == "SYMBOL" and self.tk.current_token() in OPS:
            op = self.tk.current_token()
            self._advance()
            self.compile_term()
            
            # Generate VM arithmetic
            if op == "+":   self.vm_writer.write_arithmetic("ADD")
            elif op == "-": self.vm_writer.write_arithmetic("SUB")
            elif op == "*": self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/": self.vm_writer.write_call("Math.divide", 2)
            elif op == "&": self.vm_writer.write_arithmetic("AND")
            elif op == "|": self.vm_writer.write_arithmetic("OR")
            elif op == "<": self.vm_writer.write_arithmetic("LT")
            elif op == ">": self.vm_writer.write_arithmetic("GT")
            elif op == "=": self.vm_writer.write_arithmetic("EQ")

    def compile_term(self) -> None:
        """Compile term: constants, variables, arrays, subroutine calls, expressions."""
        if self.tk.token_type() == "INT_CONST":
            value = self.tk.int_val()
            self.vm_writer.write_push("CONSTANT", value)
            self._advance()
        
        elif self.tk.token_type() == "STRING_CONST":
            value = self.tk.string_val()
            # Create String object and append characters
            self.vm_writer.write_push("CONSTANT", len(value))
            self.vm_writer.write_call("String.new", 1)
            for char in value:
                self.vm_writer.write_push("CONSTANT", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
            self._advance()
        
        elif self.tk.token_type() == "KEYWORD":
            keyword = self.tk.keyword()
            if keyword == "true":
                self.vm_writer.write_push("CONSTANT", 0)
                self.vm_writer.write_arithmetic("NOT")
            elif keyword in ["false", "null"]:
                self.vm_writer.write_push("CONSTANT", 0)
            elif keyword == "this":
                self.vm_writer.write_push("POINTER", 0)
            self._advance()
        
        elif self.tk.token_type() == "IDENTIFIER":
            identifier = self.tk.current_token()
            self._advance()
            
            if self.tk.current_token() == "[":
                # Array access: arr[index]
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index)

                self._advance()
                self.compile_expression()
                self._expect("]")

                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)
                
            elif self.tk.current_token() in ["(", "."]:
                # Subroutine call - backtrack and handle
                self.tk.current_token_index -= 1
                self.tk._cur_tok = self.tk.tokens[self.tk.current_token_index]
                self.compile_subroutine_call()
                
            else:
                # Simple variable
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index)
        
        elif self.tk.current_token() == "(":
            # Parenthesized expression
            self._advance()
            self.compile_expression()
            self._expect(")")
            
        elif self.tk.current_token() in UNARY_OPS:
            # Unary operators
            op = self.tk.current_token()
            self._advance()
            self.compile_term()
            if op == "-":
                self.vm_writer.write_arithmetic("NEG")
            elif op == "~":
                self.vm_writer.write_arithmetic("NOT")

    def compile_subroutine_call(self) -> None:
        """Compile subroutine call with proper argument handling."""
        identifier = self.tk.current_token()
        self._advance()

        n_args = 0
        if self.tk.current_token() == ".":
            # Method or function call: obj.method() or Class.function()
            self._advance()
            subroutine_name = self.tk.current_token()
            self._advance()

            if self.symbol_table.kind_of(identifier) is not None:
                # Method call on object
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index)
                n_args = 1

                class_name = self.symbol_table.type_of(identifier)
                full_name = f"{class_name}.{subroutine_name}"
            else:
                # Static function call
                full_name = f"{identifier}.{subroutine_name}"
        else:
            # Method call on current object
            subroutine_name = identifier
            self.vm_writer.write_push("POINTER", 0)
            n_args = 1 
            full_name = f"{self.class_name}.{subroutine_name}"

        self._expect("(")
        n_args += self.compile_expression_list()
        self._expect(")")

        self.vm_writer.write_call(full_name, n_args)

    def compile_expression_list(self) -> int:
        """Compile comma-separated expression list. Returns argument count."""
        n_args = 0
        if not (self.tk.token_type() == "SYMBOL" and self.tk.current_token() == ")"):
            self.compile_expression()
            n_args = 1
        
            while self.tk.current_token() == ",":
                self._advance()
                self.compile_expression()
                n_args += 1
        
        return n_args

    def _kind_to_segment(self, kind: str) -> str:
        """Convert symbol table kind to VM segment."""
        segment_map = {
            "STATIC": "STATIC",
            "FIELD": "THIS", 
            "ARG": "ARG",
            "VAR": "LOCAL"
        }
        return segment_map.get(kind, "TEMP")