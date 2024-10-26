from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage for rules
rules_db = []  # This will act as our in-memory database

# Abstract Syntax Tree (AST) Node class
class ASTNode:
    def __init__(self, node_type, left=None, right=None, attribute=None, value=None):
        self.node_type = node_type
        self.left = left
        self.right = right
        self.attribute = attribute
        self.value = value

# Function to evaluate the AST
def evaluate_ast(node, user_data):
    if node.node_type == 'comparison':
        attribute_value = user_data.get(node.attribute)
        if attribute_value is None:
            return False  # Handle NoneType attribute value
        if isinstance(node.value, int):
            return attribute_value > node.value
        elif isinstance(node.value, str):
            return attribute_value == node.value  # For string comparison
        return False  # Add more checks as needed
    elif node.node_type == 'logical_and':
        return evaluate_ast(node.left, user_data) and evaluate_ast(node.right, user_data)
    elif node.node_type == 'logical_or':
        return evaluate_ast(node.left, user_data) or evaluate_ast(node.right, user_data)

# Function to parse the rule string into an AST
def parse_rule_string(rule_string):
    rule_string = rule_string.strip()
    
    # Handle logical AND
    if " AND " in rule_string:
        parts = rule_string.split(" AND ")
        left = parse_rule_string(parts[0])
        right = parse_rule_string(" AND ".join(parts[1:]))
        return ASTNode('logical_and', left, right)
    
    # Handle logical OR
    elif " OR " in rule_string:
        parts = rule_string.split(" OR ")
        left = parse_rule_string(parts[0])
        right = parse_rule_string(" OR ".join(parts[1:]))
        return ASTNode('logical_or', left, right)
    
    else:
        # Handle comparisons
        operators = ['>', '<', '=', '>=', '<=', '!=']
        for op in operators:
            if op in rule_string:
                attr, op_value = rule_string.split(op)
                attr = attr.strip()
                op_value = op_value.strip().rstrip(')')  # Remove any trailing parentheses

                # Check if op_value is a number or a string and parse accordingly
                if op_value.startswith("'") and op_value.endswith("'"):
                    value = op_value[1:-1]  # Remove quotes for string values
                else:
                    # Attempt to convert to int or keep as string
                    try:
                        value = int(op_value)  # Convert to int for numerical comparisons
                    except ValueError:
                        value = op_value  # Keep as string if conversion fails

                return ASTNode('comparison', attribute=attr, value=value)

        raise ValueError("Invalid rule format")

# Route to create a rule
@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.get_json()
    rule_string = data.get('rule_string')
    
    try:
        ast = parse_rule_string(rule_string)
        
        # Store the rule in in-memory storage
        rules_db.append({"rule_string": rule_string, "ast": ast})  # Store the rule string and AST
        
        return jsonify({"message": "Rule created successfully!", "rule": rule_string}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Route to evaluate a rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.get_json()
    ast = data.get('ast')  # Assuming ast is passed in a suitable format
    user_data = data.get('user_data', {})  # Fetch user data, default to empty dict

    # Ensure the AST is reconstructed correctly from its string representation
    if ast is None or user_data is None:
        return jsonify({"error": "AST or user data is missing"}), 400

    # Reconstruct AST from the string if necessary
    reconstructed_ast = reconstruct_ast(ast)
    
    result = evaluate_ast(reconstructed_ast, user_data)
    return jsonify({"result": result}), 200

# Function to reconstruct AST from the provided representation
def reconstruct_ast(ast):
    if isinstance(ast, dict):
        node_type = ast.get('node_type')
        left = reconstruct_ast(ast.get('left')) if 'left' in ast else None
        right = reconstruct_ast(ast.get('right')) if 'right' in ast else None
        return ASTNode(node_type, left, right, ast.get('attribute'), ast.get('value'))
    return None

# Home route for testing
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
