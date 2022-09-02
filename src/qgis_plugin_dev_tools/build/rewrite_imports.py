import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class SpecialImportRewriter(ast.NodeTransformer):
    """
    Transformer class to rewrite simple "import module.x.y" style imports
    to vendored format, for example "import something._vendor.module.x.y".
    """

    from_module: str
    to_module: str

    _replaced_imported_names: Dict[str, str] = field(default_factory=dict, init=False)

    # collect the found imported names to replace the references also
    def visit_Import(self, node: ast.Import) -> Any:  # noqa N802
        for alias in node.names:
            if alias.name.startswith(f"{self.from_module}.") and alias.asname is None:
                old_module_name = alias.name
                new_identifier_name = "vendored_" + alias.name.replace(".", "_")
                self._replaced_imported_names[old_module_name] = new_identifier_name
                child_module_names = old_module_name.replace(
                    f"{self.from_module}.", "", 1
                )
                alias.name = f"{self.to_module}.{child_module_names}"
                alias.asname = new_identifier_name
        return node

    # check the attributes for an imported module name reference
    def visit_Attribute(self, node: ast.Attribute) -> Any:  # noqa N802
        attribute_name = ast.unparse(node)
        if attribute_name in self._replaced_imported_names:
            replaced_name = self._replaced_imported_names[attribute_name]
            return ast.Name(id=replaced_name, ctx=ast.Load())

        return self.generic_visit(node)

    # this will only handle sys.modules['something'] replace
    def visit_Subscript(self, node: ast.Subscript) -> Any:  # noqa N802
        if (
            ast.unparse(node.value) == "sys.modules"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
            and node.slice.value.startswith(f"{self.from_module}.")
        ):
            child_module_names = node.slice.value.replace(f"{self.from_module}.", "", 1)
            node.slice.value = f"{self.to_module}.{child_module_names}"
            return node

        return self.generic_visit(node)


def rewrite_imports_in_source_file(
    source_file: Path, rewritten_package_name: str, container_package_name: str
) -> None:
    contents = source_file.read_text(encoding="utf-8")

    # special case where a submodule of the vendored package is imported
    # or the name is defined in a sys.modules key as a constant
    specials = [
        f"import {rewritten_package_name}.",
        f"sys.modules['{rewritten_package_name}.",
        f'sys.modules["{rewritten_package_name}.',
    ]
    if any(special in contents for special in specials):

        # hold on to the original for license comments
        # since comments are lost with ast parse+unparse
        orig_file = source_file.with_name(source_file.name + "_original")
        orig_file.write_text(contents, encoding="utf-8")
        original_note = f"# parsed with ast, see original {orig_file.name}\n\n"

        tree = ast.parse(contents)
        new_tree = ast.fix_missing_locations(
            SpecialImportRewriter(
                from_module=rewritten_package_name,
                to_module=f"{container_package_name}.{rewritten_package_name}",
            ).visit(tree)
        )
        contents = original_note + ast.unparse(new_tree)

    # trivial cases with valid identifiers
    contents = contents.replace(
        f"from {rewritten_package_name} import",
        f"from {container_package_name}.{rewritten_package_name} import",
    )
    contents = contents.replace(
        f"from {rewritten_package_name}.",
        f"from {container_package_name}.{rewritten_package_name}.",
    )

    # package name with a trailing dot is handled in special case above,
    # this case only needs to handle imports, not from-imports, since
    # otherwise plain replace will match "import package" also in a format
    # "from x import package"

    contents = re.sub(
        r"(^|;)([\s\t]*)" + f"import {rewritten_package_name} as",
        f"\\1\\2import {container_package_name}.{rewritten_package_name} as",
        contents,
    )

    contents = re.sub(
        r"(^|;)([\s\t]*)" + f"import {rewritten_package_name}",
        (
            f"\\1\\2import {container_package_name}.{rewritten_package_name} "
            f"as {rewritten_package_name}"
        ),
        contents,
        flags=re.M,
    )

    source_file.write_text(contents, encoding="utf-8")


def insert_as_first_import(plugin_init_file: Path, import_string: str) -> None:
    contents = plugin_init_file.read_text(encoding="utf-8")
    contents = f"import {import_string}\n" + contents
    plugin_init_file.write_text(contents, encoding="utf-8")
