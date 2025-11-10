import os
import argparse

class Node:
    def __init__(self, name: str, is_dir: bool, level: int):
        self.name = name
        self.is_dir = is_dir  # True if directory, False if file
        self.children = []
        self.level = level  # Indentation Level

    def add_child(self, child_node):
        self.children.append(child_node)


def parse_markdown(markdown_text: str) -> list[tuple[str, int]]:
    """Parses Markdown text into a list of (name, level) tuples."""
    entries = []
    for line in markdown_text.splitlines():
        line = line.rstrip()  # Remove trailing whitespace
        if not line:
            continue  # Skip empty lines

        level = 0
        for char in line:
            if char == ' ':
                level += 1
            else:
                break

        name = line[level:].strip()
        entries.append((name, level))
    return entries


def build_tree(entries: list[tuple[str, int]]) -> Node:
    """Builds a tree structure from a list of (name, level) tuples."""
    if not entries:
        return None  # Handle empty input

    root_node = Node(entries[0][0], True, entries[0][1])  # Assume first entry is root
    stack = [root_node]

    for name, level in entries[1:]:
        is_dir = name.endswith("/")
        node = Node(name, is_dir, level)

        while stack and level <= stack[-1].level:
            stack.pop()

        if stack:
            stack[-1].add_child(node)
        stack.append(node)

    return root_node


def generate_tree_text(root_node: Node, indent_str: str = "    ",
                      branch_str: str = "├── ", last_branch_str: str = "└── ") -> str:
    """Generates tree-text from a tree structure."""

    def _generate_tree_text_recursive(node: Node, prefix: str, is_last: bool) -> str:
        result = prefix
        if is_last:
            result += last_branch_str
        else:
            result += branch_str
        # if node.is_dir:
        #     print(node.name)
        result += node.name[:-1] + ("/" if node.is_dir else "") + "\n"

        for i, child in enumerate(node.children):
            next_prefix = prefix + (indent_str if is_last else "│" + indent_str)
            result += _generate_tree_text_recursive(child, next_prefix, i == len(node.children) - 1)
        return result

    if not root_node:
        return ""
    return _generate_tree_text_recursive(root_node, "", True)


def parse_tree_text(tree_text: str, indent_str: str = "    ") -> list[tuple[str, int]]:
    """Parses tree-text into a list of (name, level) tuples.

    Args:
        tree_text: The tree-text string.
        indent_str: The string used for indentation (default: "    ").

    Returns:
        A list of (name, level) tuples.
    """
    entries = []
    indent_len = len(indent_str)

    for line in tree_text.splitlines():
        line = line.rstrip()
        if not line:
            continue

        level = 0
        name_start = 0
        current_indent = 0  # Track indentation within the current unit

        for i, char in enumerate(line):
            if char in (' ', '│', '├', '└', '─', '    '):  # Include tree-drawing chars
                    name_start = i + 1
            if char == ' ':
                current_indent += 1
                if current_indent == indent_len:
                    level += 1
                    current_indent = 0

        for i, char in enumerate(line):
            if char in ('│', '├', '└'):
                level += 1
                break

        name = line[name_start:].strip()
        entries.append((name, level))
    return entries

def generate_markdown(root_node: Node) -> str:
    """Generates Markdown from a tree structure."""

    def _generate_markdown_recursive(node: Node, level: int) -> str:
        if(level == -1):
            result = ""
        else:
            print(node.name, level)
            result = "    " * level + node.name + "\n"
        for child in node.children:
            result += _generate_markdown_recursive(child, child.level)
        return result

    if not root_node:
        return ""
    return _generate_markdown_recursive(root_node, 0)  # Start at level 0


def construct_markdown_structure(markdown_text: str) -> Node:
    """Converts Markdown to tree-text."""
    entries = parse_markdown(markdown_text)
    if not entries:
      return ""
    tree = build_tree(entries)
    return tree


def construct_tree_structre(tree_text: str) -> Node:
    """Converts tree-text to Markdown."""
    entries = parse_tree_text(tree_text)
    if not entries:
      return ""
    tree = build_tree(entries)
    return tree

def create_files_and_dirs(node, current_path):
    """Recursively creates files and directories based on the Node tree."""
    path = os.path.join(current_path, node.name)
    if node.is_dir:
        os.makedirs(path, exist_ok=True)
        for child in node.children:
            create_files_and_dirs(child, path)
    else:
        if not os.path.exists(path): # prevents overwriting of the files.
            open(path, 'w').close()  # Create empty file

def detect_input_type(input_text, file_extension):
    """Detects input type (markdown or tree) based on content and extension."""

    # Prioritize file extension if provided
    if file_extension:
        file_extension = file_extension.lower()
        if file_extension == ".md":
            return "markdown"
        elif file_extension in (".txt", ".tree"):  # Common tree extensions
            return "tree"

def main():
    parser = argparse.ArgumentParser(description="Create directory structure from text.")
    # parser.add_argument("tree_text", help="The tree-like text representation.")
    parser.add_argument("input_file", help="Path to the input file (Markdown or tree).")
    parser.add_argument("-r", "--root_dir", default=".", help="Root directory (default: current directory)")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.")
        return
    print(args.input_file, input_text, args.root_dir)

    file_extension = os.path.splitext(args.input_file)[1]  # Get file extension
    input_type = detect_input_type(input_text, file_extension)
    if input_type == "markdown":
        tree = construct_markdown_structure(input_text)
    elif input_type == "tree":
        tree = construct_tree_structre(input_text)
    else:
        print("Error: Could not automatically detect input type.  Use -m2t or -t2m.")
        return
    
    create_files_and_dirs(tree, args.root_dir)
    print(f"Directory structure created in '{os.path.abspath(args.root_dir)}'")


if __name__ == "__main__":
    main()