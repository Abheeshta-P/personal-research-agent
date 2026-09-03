from langchain_core.tools import tool


@tool
def calculator(a: float, b: float, operation: str) -> str:
    """Perform a calculation on two numbers. Operation can be add, subtract, multiply, or divide."""

    # Execute supported arithmetic operations
    if operation == "add":
        return str(a + b)

    if operation == "subtract":
        return str(a - b)

    if operation == "multiply":
        return str(a * b)

    if operation == "divide":
        # Return friendly error message instead of raising an unhandled exception
        if b == 0:
            return "Error: Cannot divide by zero."
        return str(a / b)

    # Return error string for unrecognized operations so the agent can inform the user
    return f"Error: Unknown operation '{operation}'. Use add, subtract, multiply, or divide."