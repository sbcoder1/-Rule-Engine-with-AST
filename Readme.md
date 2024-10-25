# Rule Engine with Abstract Syntax Tree (AST)

This project is a Rule Engine built using Flask that evaluates user eligibility based on specified rules. It uses an Abstract Syntax Tree (AST) to represent conditional rules, allowing dynamic creation, combination, and modification of rules.

## Features

- **Dynamic Rule Creation**: Users can create complex rules with logical operators (`AND`, `OR`) and comparison operators.
- **AST Evaluation**: Rules are parsed into an AST for structured and efficient evaluation.
- **In-memory Storage**: Rules are temporarily stored in local storage to simplify prototyping.
- **User Data Evaluation**: Each rule is evaluated against user data, determining eligibility based on rule logic.

## Requirements

To install the required dependencies, run:

```bash
pip install -r requirements.txt
