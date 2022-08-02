# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, GatherImportsVisitor, ImportItem
from stubber.cst_transformer import StubTypingCollector, update_def_docstr, update_module_docstr, TypeInfo, MODULE_KEY

##########################################################################################
log = logging.getLogger(__name__)
#########################################################################################


class MergeCommand(VisitorBasedCodemodCommand):
    """
    A libcst transformer that merges the type-rich information from a doc-stub into
    a firmware stub.
    The resulting file will contain information from both sources.

    - module docstring - from source

    - function parameters and types - from docstubs
    - function return types - from docstubs
    - function docstrings - from source

    """

    DESCRIPTION: str = "Merge the type-rich information from a doc-stub into a firmware stub"

    @staticmethod
    def add_args(arg_parser: argparse.ArgumentParser) -> None:
        """Add command-line args that a user can specify for running this codemod."""

        arg_parser.add_argument(
            # "-sf",
            "--stubfile",
            dest="stub_file",
            metavar="PATH",
            help="The path to the doc-stub file",
            type=str,
            required=True,
        )

    def __init__(self, context: CodemodContext, stub_file: Union[Path, str]) -> None:
        super().__init__(context)
        # stack for storing the canonical name of the current function/method
        self.stack: List[str] = []
        # stubfile is the path to the doc-stub file
        self.stub_path = Path(stub_file)
        # read the stub file from the path
        self.stub_source = self.stub_path.read_text(encoding="utf-8")
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            TypeInfo,  # value: TypeInfo
        ] = {}

        self.stub_imports: Dict[str, ImportItem] = {}
        # parse the doc-stub file
        if self.stub_source:
            # parse the doc-stub file
            stub_tree = cst.parse_module(self.stub_source)
            # create the collectors
            typing_collector = StubTypingCollector()
            import_collector = GatherImportsVisitor(context)
            # visit the doc-stub file with all collectors
            stub_tree.visit(typing_collector)
            self.annotations = typing_collector.annotations

            # Store the imports that were added to the stub file
            stub_tree.visit(import_collector)
            self.stub_imports = import_collector.symbol_mapping

    # ------------------------------------------------------------------------

    def leave_Module(self, node: cst.Module, updated_node: cst.Module) -> cst.Module:
        "Update the Module docstring"
        # add any needed imports from the doc-stub
        for k in self.stub_imports.keys():
            _imp = self.stub_imports[k]
            log.debug(f"import {k} = {_imp}")
            AddImportsVisitor.add_needed_import(
                self.context,
                module=_imp.module_name,
                obj=_imp.obj_name,
                asname=_imp.alias,
                relative=_imp.relative,
            )

        # update the docstring.
        if not MODULE_KEY in self.annotations:
            # no changes
            return updated_node

        # update/replace  module docstrings
        # todo: or should we add / merge the docstrings?
        new = self.annotations[MODULE_KEY]

        return update_module_docstr(updated_node, new.docstr_node)

    # ------------------------------------------------------------
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        stack_id = tuple(self.stack)
        self.stack.pop()
        if not stack_id in self.annotations:
            # no changes to the function
            return updated_node
        # update the firmware_stub from the doc_stub information
        new = self.annotations[stack_id]
        # first update the docstring
        updated_node = update_def_docstr(updated_node, new.docstr_node)
        # Sometimes the firmware stubs and the doc stubs have different types : FunctionDef / ClassDef
        # we need to be carefull not to copy over all the annotations if the types are different
        if new.def_type == "classdef":
            # Same type, we can copy over all the annotations
            return updated_node.with_changes(decorators=new.decorators)
        elif new.def_type == "funcdef":
            # Different type: ClassDef --> FuncDef ,
            # for now just return the updated node
            return updated_node
        else:
            #  just return the updated node
            return updated_node

    # ------------------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return True

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        "Update the function Parameters and return type, decorators and docstring"

        stack_id = tuple(self.stack)
        self.stack.pop()
        if not stack_id in self.annotations:
            # no changes to the function
            return updated_node
        # update the firmware_stub from the doc_stub information
        new = self.annotations[stack_id]

        # first update the docstring
        updated_node = update_def_docstr(updated_node, new.docstr_node)
        # Sometimes the firmware stubs and the doc stubs have different types : FunctionDef / ClassDef
        # we need to be carefull not to copy over all the annotations if the types are different
        if new.def_type == "funcdef":
            # Same type, we can copy over all the annotations
            return updated_node.with_changes(
                params=new.params,
                returns=new.returns,
                decorators=new.decorators,
            )
        elif new.def_type == "classdef":
            # Different type: ClassDef --> FuncDef ,
            # for now just return the updated node
            return updated_node
        else:
            #  just return the updated node
            return updated_node