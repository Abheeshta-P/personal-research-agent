from langchain_core.tools import tool


@tool
def calculator(a: float, b: float, operation: str) -> float:
    """Perform a calculation on two numbers. Operation can be add, subtract, multiply, or divide."""

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    raise ValueError(
        "Unknown operation. Use add, subtract, multiply, or divide."
    )