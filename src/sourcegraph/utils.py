import ast
import os
import tempfile

import networkx as nx
import streamlit as st
from git import Repo

__all__ = ["repo_to_graph", "get_all_dependent_functions"]


def read_file_content(blob):
    try:
        return blob.data_stream.read().decode('utf-8')
    except UnicodeDecodeError:
        return "[Binary file]"


def process_tree(tree, path=""):
    result = []
    for item in tree.traverse():
        if item.name.endswith(".csv"):
            continue
        if item.type == 'blob' and item.name.endswith(".py"):
            file_content = read_file_content(item)
            result.append({
                "type": "file",
                "name": os.path.join(path, item.name),
                "content": file_content
            })
        elif item.type == 'tree':
            result.extend(process_tree(item, os.path.join(path, item.name)))
    return result


def extract_definitions_from_code(file_content, file_name):
    definitions = []
    try:
        tree = ast.parse(file_content)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                definition_name = node.name
                definition = ast.unparse(node)
                docstring = ast.get_docstring(node)
                definitions.append({
                    "type": "function",
                    "name": definition_name,
                    "definition": definition,
                    "file_name": file_name,
                    "docstring": docstring
                })
            elif isinstance(node, ast.ClassDef):
                definition_name = node.name
                definition = ast.unparse(node)
                docstring = ast.get_docstring(node)
                definitions.append({
                    "type": "class",
                    "name": definition_name,
                    "definition": definition,
                    "file_name": file_name,
                    "docstring": docstring
                })
    except Exception as e:
        st.error(f"Error parsing code in file {file_name}: {e}")

    return definitions


def resolve_relative_imports(code, current_file_path, repo_root_path):
    resolved_imports = set()
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level > 0:  # This is a relative import
                    current_dir = os.path.dirname(current_file_path)
                    for _ in range(node.level - 1):
                        current_dir = os.path.dirname(current_dir)
                    if node.module:
                        module_path = os.path.join(current_dir, *node.module.split('.'))
                    else:
                        module_path = current_dir
                    py_file = f"{module_path}.py"
                    init_file = os.path.join(module_path, "__init__.py")
                    if os.path.exists(py_file):
                        resolved_imports.add(py_file)
                    elif os.path.exists(init_file):
                        resolved_imports.add(init_file)
    except Exception as e:
        st.error(f"Error resolving imports in file {current_file_path}: {e}")

    return resolved_imports


def extract_definitions_from_files(files):
    all_definitions = []
    repo_root_path = os.path.commonpath([file['name'] for file in files])

    for file in files:
        definitions = extract_definitions_from_code(file["content"], file["name"])
        all_definitions.extend(definitions)

        # Handle relative imports
        resolved_imports = resolve_relative_imports(file["content"], file["name"], repo_root_path)
        for import_path in resolved_imports:
            if import_path not in [f['name'] for f in files]:
                with open(import_path, 'r', encoding='utf-8') as imported_file:
                    imported_code = imported_file.read()
                imported_definitions = extract_definitions_from_code(imported_code, import_path)
                all_definitions.extend(imported_definitions)

    return all_definitions


def find_calls_and_classes(code, defined_functions, defined_classes):
    called_functions = set()
    used_classes = set()
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in defined_functions:
                    called_functions.add(node.func.id)
                elif isinstance(node.func, ast.Attribute) and node.func.attr in defined_functions:
                    called_functions.add(node.func.attr)
            elif isinstance(node, ast.Name) and node.id in defined_classes:
                used_classes.add(node.id)
            elif isinstance(node, ast.Attribute) and node.attr in defined_classes:
                used_classes.add(node.attr)
    except Exception as e:
        st.error(f"Error parsing code: {e}")

    return called_functions, used_classes


def build_graph_data(definitions):
    defined_function_names = {d["name"] for d in definitions if d["type"] == "function"}
    defined_class_names = {d["name"] for d in definitions if d["type"] == "class"}
    nodes = {d["name"]: d for d in definitions}
    edges = []

    for definition in definitions:
        if definition["type"] in ["function", "class"]:
            called_functions, used_classes = find_calls_and_classes(definition["definition"], defined_function_names,
                                                                    defined_class_names)
            for called_function in called_functions:
                edges.append((definition["name"], called_function))
            for used_class in used_classes:
                edges.append((definition["name"], used_class))

    return nodes, edges


def create_networkx_graph(nodes, edges):
    graph = nx.DiGraph()
    for node, attrs in nodes.items():
        graph.add_node(node, **{k: str(v) if v is not None else "" for k, v in attrs.items()})
    for edge in edges:
        graph.add_edge(edge[0], edge[1])
    return graph


def repo_to_graph(repo_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        repo = Repo.clone_from(repo_url, temp_dir)
        head_commit = repo.head.commit
        tree = head_commit.tree

        files = process_tree(tree)
        definitions = extract_definitions_from_files(files)
        nodes, edges = build_graph_data(definitions)

        graph = create_networkx_graph(nodes, edges)
        return graph


def get_all_dependent_functions(graph, start_node):
    """
    Get all functions that are directly or indirectly called by the start_node.
    """
    dependent_functions = set()
    to_visit = [start_node]
    while to_visit:
        current_node = to_visit.pop(0)
        for neighbor in graph.successors(current_node):
            if neighbor not in dependent_functions:
                dependent_functions.add(neighbor)
                to_visit.append(neighbor)
    return dependent_functions
