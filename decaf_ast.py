# List of tables to build AST
class class_record():
    def __init__(self, class_name = None):
        self.class_name = class_name
        self.lineno = None
        self.super_name = None
        self.constructors = []
        self.methods = []
        self.fields = []

class constructor_record():
    def __init__(self):
        self.constructor_id = None
        self.constructor_visibility = None
        self.constructor_parameters = []
        self.variable_table = []
        self.constructor_body = None

class method_record():
    def __init__(self, method_name = "", method_id = None, containing_class = "", method_visibility = "", method_applicability = "",
                 method_parameters = [], return_type = None, variable_table = []):
        self.method_name = method_name
        self.method_id = method_id
        self.containing_class = containing_class # is filled in by the class declaration function
        self.method_visibility = method_visibility
        self.method_applicability = method_applicability
        self.method_parameters = method_parameters # series of references to variables in the variable table
        self.return_type = return_type # instance of a type record
        self.variable_table = variable_table
        self.method_body = None # instance of a statement record

class field_record():
    def __init__(self):
        self.field_name = ""
        self.lineno = None
        self.field_id = None
        self.containing_class = None
        self.field_visibility = ""
        self.field_applicability = ""
        self.type = None

class variable_record():
    def __init__(self, variable_name = None, variable_id = None, variable_kind = None, type = None):
        self.variable_name = variable_name
        self.lineno = None
        self.variable_id = variable_id
        self.variable_kind = variable_kind
        self.type = type

class type_record():
    def __init__(self, type = None):
        self.type = type

# ==================================================================
# Statements

class statement_record():
    def __init__(self, type):
        self.line_range = ()
        self.type = type
        self.isTypeCorrect = None

class if_statement(statement_record):
    def __init__(self):
        super().__init__("If")
        self.if_cond = None
        self.then_part = None
        self.else_part = None

class while_statement(statement_record):
    def __init__(self):
        super().__init__("While")
        self.loop_cond = None
        self.loop_body = None
    
class for_statement(statement_record):
    def __init__(self):
        super().__init__("For")
        self.initializer = None
        self.loop_cond = None
        self.update_expr = None
        self.loop_body = None

class return_statement(statement_record):
    def __init__(self):
        super().__init__("Return")
        self.return_value = None

class expression_statement(statement_record):
    def __init__(self):
        super().__init__("Expr")
        self.expression = None

class block_statement(statement_record):
    def __init__(self):
        super().__init__("Block")
        self.statements = []

class break_statement(statement_record):
    def __init__(self):
        super().__init__("Break")

class continue_statement(statement_record):
    def __init__(self):
        super().__init__("Continue")

class skip_statement(statement_record):
    def __init__(self):
        super().__init__("Skip")

class var_decl_statement(statement_record):
    def __init__(self):
        super().__init__("Var_decl")
        self.var_decls = [] # stores an array of variable records declared on a line

# Statements
# ==================================================================

# ==================================================================
# Expressions

class expression_record():
    def __init__(self, expr_type):
        self.line_range = ()
        self.expr_type = expr_type # string denoting kind of expression
        self.data_type = None

class constant_expression(expression_record):
    def __init__(self):
        super().__init__("Constant")
        self.value = None

class var_expression(expression_record):
    def __init__(self):
        super().__init__("Variable")
        self.id = None # int
        self.name = None # string

class unary_expression(expression_record):
    def __init__(self):
        super().__init__("Unary")
        self.operand = None
        self.operator = "" # string denoting operator (uminus or neg)

class binary_expression(expression_record):
    def __init__(self, op1, op2, operator):
        super().__init__("Binary")
        self.fst_operand = op1
        self.snd_operand = op2
        self.operator = operator # add, sub, mul, div, and, or, eq, neq, lt, leq, gt, geq

class assign_expression(expression_record):
    def __init__(self):
        super().__init__("Assign")
        self.lhs = None
        self.rhs = None

class auto_expression(expression_record):
    def __init__(self):
        super().__init__("Auto")
        self.operand = None
        self.auto = "" # string denoting auto-increment ("++") or auto-decrement ("--")
        self.fix = "" # string denoting either "prefix" or "postfix"

class field_access_expression(expression_record):
    def __init__(self):
        super().__init__("Field-access")
        self.base = None
        self.field_name = ""
        self.accessed_id = None

class method_call_expression(expression_record):
    def __init__(self):
        super().__init__("Method-call")
        self.base = None
        self.method_name = ""
        self.arguments = [] # an array of expressions denoting the arguments to the method call. May be empty
        self.accessed_id = None

class new_object_expression(expression_record):
    def __init__(self):
        super().__init__("New-object")
        self.base = ""
        self.arguments = [] # an array of expressions denoting the arguments to the constructor. May be empty
        self.accessed_id = None

class this_expression(expression_record):
    def __init__(self):
        super().__init__("This")

class super_expression(expression_record):
    def __init__(self):
        super().__init__("Super")

class class_reference_expression(expression_record):
    def __init__(self, referred_class_name):
        super().__init__("Class-reference")
        self.referred_class_name = referred_class_name # Denotes the value of literal class names

# Expressions
# ==================================================================

# ===============================================================
# Printing

def print_class_table(class_table):
    
    # table contains only in and out (empty program)
    if len(class_table) <= 2:
        print("Empty program.")
        return
    
    for record in class_table:
        print("-----------------------------------------------------------")
        print_class(record)
    print("-----------------------------------------------------------")

def print_class(c):
    print("Class Name: " + c.class_name)
    if c.super_name == None:
        print("Superclass Name: ") 
    else:
        print("Superclass Name: " + c.super_name)
    
    print("Fields:")
    for field in c.fields:
        print_field(field)
        print()
    
    print("Constructors:")
    for constructor in c.constructors:
        print_constructor(constructor)
        print()

    print("Methods:")
    for method in c.methods:
        print_method(method)
        print()

def print_field(field):
    print("FIELD: " + str(field.field_id) + ", " 
          + str(field.field_name) + ", " 
          + str(field.containing_class) + ", " 
          + str(field.field_visibility) + ", " 
          + str(field.field_applicability) + ", "
          + str(field.type.type), end = "")

def print_constructor(constructor):
    print("CONSTRUCTOR: " + str(constructor.constructor_id) + ", " 
          + str(constructor.constructor_visibility))
    
    print("Constructor Parameters: ", end = "")
    for i in range(len(constructor.constructor_parameters)):
        print(constructor.constructor_parameters[i].variable_id, end = "")
        if i < len(constructor.constructor_parameters)-1:
            print(", ", end = "")
    print()

    print("Variable Table: ")
    for i in range(len(constructor.variable_table)):
        print_variable(constructor.variable_table[i])
        print()

    print("Constructor Body: ", end = "")
    print_statement(constructor.constructor_body)

def print_method(method):
    print("METHOD: " + str(method.method_id) + ", " 
          + str(method.method_name) + ", " 
          + str(method.containing_class) + ", " 
          + str(method.method_visibility) + ", " 
          + str(method.method_applicability) + ", "
          + str(method.return_type.type))
    
    print("Method Parameters: ", end = "")
    for i in range(len(method.method_parameters)):
        print(method.method_parameters[i].variable_id, end = "")
        if i < len(method.method_parameters)-1:
            print(", ", end = "")
    print()

    print("Variable Table: ")
    for i in range(len(method.variable_table)):
        print_variable(method.variable_table[i])
        print()

    print("Method Body: ", end = "")
    print_statement(method.method_body)

# Print statement
def print_statement(statement):

    if statement == None:
        return

    print()
    print(statement.type + "(", end = "")

    if type(statement) == if_statement:
        print_if_statement(statement)
    if type(statement) == while_statement:
        print_while_statement(statement)
    if type(statement) == for_statement:
        print_for_statement(statement)
    if type(statement) == return_statement:
        print_return_statement(statement)
    if type(statement) == expression_statement:
        print_expression_statement(statement)
    if type(statement) == block_statement:
        print_block_statement(statement)

    print(")", end = "")

def print_if_statement(statement):
    print_expression(statement.if_cond)
    print(", ", end = "")
    print_statement(statement.then_part)
    print(", ", end = "")
    print_statement(statement.else_part)

def print_while_statement(statement):
    print_expression(statement.loop_cond)
    print(", ", end = "")
    print_statement(statement.loop_body)

def print_for_statement(statement):
    print_statement(statement.initializer)
    print(", ", end = "")
    print_expression(statement.loop_cond)
    print(", ", end = "")
    print_statement(statement.update_expr)
    print(", ", end = "")
    print_statement(statement.loop_body)

def print_return_statement(statement):
    print_expression(statement.return_value)

def print_expression_statement(statement):
    print_expression(statement.expression)

def print_block_statement(statement):
    print("[", end = "")
    for i in range(len(statement.statements)):
        if type(statement.statements[i]) != var_decl_statement:
            print_statement(statement.statements[i])
            if i < len(statement.statements)-1:
                print(", ", end = "")
    print()
    print("]", end = "")

# Printing expression
def print_expression(expression):
    if expression == None:
        return
    
    print(expression.expr_type, end = "")

    if type(expression) == constant_expression:
        print_constant_expression(expression)
    elif type(expression) == var_expression:
        print_var_expression(expression)
    elif type(expression) == unary_expression:
        print_unary_expression(expression)
    elif type(expression) == binary_expression:
        print_binary_expression(expression)
    elif type(expression) == assign_expression:
        print_assign_expression(expression)
    elif type(expression) == auto_expression:
        print_auto_expression(expression)
    elif type(expression) == field_access_expression:
        print_field_access_expression(expression)
    elif type(expression) == method_call_expression:
        print_method_call_expression(expression)
    elif type(expression) == new_object_expression:
        print_new_object_expression(expression)
    elif type(expression) == class_reference_expression:
        print_class_reference_expression(expression)

def print_constant_expression(expression):
    print("(", end = "")

    if expression.value == "true" or expression.value == "false" or expression.value == "null":
        print(expression.value.capitalize(), end = ")")
        return
    if type(expression.value) == int:
        print("Integer-constant", end = "")
    elif type(expression.value) == float:
        print("Float-constant", end = "")
    elif expression.value != "true" and expression.value != "false" and expression.value != "null":
        print("String-constant", end = "")
    print("(" + str(expression.value) + ")", end = "")

    print(")", end = "")

def print_var_expression(expression):
    print("(", end = "")

    print(expression.id, end = "")

    print(")", end = "")

def print_unary_expression(expression):
    print("(", end = "")

    print(str(expression.operator) + ", ", end = "")
    print_expression(expression.operand)

    print(")", end = "")

def print_binary_expression(expression):
    print("(", end = "")

    print(str(expression.operator) + ", ", end = "")
    print_expression(expression.fst_operand)
    print(", ", end = "")
    print_expression(expression.snd_operand)

    print(")", end = "")

def print_assign_expression(expression):
    print("(", end = "")

    print_expression(expression.lhs)
    print(", ", end = "")
    print_expression(expression.rhs)

    print(")", end = "")

def print_auto_expression(expression):
    print("(", end = "")
    
    print_expression(expression.operand)
    print(", " + str(expression.auto) + ", " + str(expression.fix), end = "")

    print(")", end = "")

def print_field_access_expression(expression):
    print("(", end = "")

    print_expression(expression.base)
    print(", " + str(expression.field_name), end = "")

    print(")", end = "")

def print_method_call_expression(expression):
    print("(", end = "")

    print_expression(expression.base)
    print(", " + str(expression.method_name) + ", [", end = "")
    for arg in expression.arguments:
        print_expression(arg)
    print("]", end = "")

    print(")", end = "")

def print_new_object_expression(expression):
    print("(", end = "")

    print(str(expression.base) + ", [", end = "")
    for arg in expression.arguments:
        print_expression(arg)
    print("]", end = "")

    print(")", end = "")

def print_class_reference_expression(expression):
    print("(", end = "")

    print(str(expression.referred_class_name), end = "")

    print(")", end = "")

def print_variable(variable):
     print("VARIABLE: " + str(variable.variable_id) + ", " + str(variable.variable_name) + ", " 
           + str(variable.variable_kind) + ", " + str(variable.type.type), end = "")
    
# Printing
# ===============================================================