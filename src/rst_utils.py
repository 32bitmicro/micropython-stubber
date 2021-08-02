""" Work in Progress  

Tries to determine the return type by parsing the docstring and the function signature
 - if the signature contains a return type --> <something> then that is returned
 - check a lookup dictionary of type overrides, 
    if the functionnae is listed, then use the override
 - use re to find phrases such as:
    - 'Returns ..... '
    - 'Gets  ..... '
 - docstring is joined without newlines to simplify parsing
 - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
 - builds a list return type candidates 
 - selects the highest ranking candidate 
 - the default Type is 'Any'
 

todo: 

    - regex :
        - 'With no arguments the frequency in Hz is returned.'
        - 'Get or set' --> indicates overloaded/optional return Union[None|...]
        - add regex for 'Query' ` Otherwise, query current state if no argument is provided. `

    - regex :
        - 'With no arguments the frequency in Hz is returned.'
        - 'Get or set' --> indicates overloaded/optional return Union[None|...]
        - add regex for 'Query' ` Otherwise, query current state if no argument is provided. `

    - try if an Azure Machine Learning works as well 
        https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources
    - 
"""
# ref: https://regex101.com/codegen?language=python
# https://regex101.com/r/Ni8g2z/1


import json
from pathlib import Path
import re
from typing import Dict, List, Tuple, Union
from rst_lookup import LOOKUP_LIST


def distill_return(return_text: str) -> List[Dict]:
    """Find return type and confidence.
    Returns a list of possible types and confidence weighting.
        {
            type :str               # the return type
            confidence: float       # the confidence between 0.0 and 1
            match: Optional[str]    # for debugging : the reason the match was made
          }

    """
    candidates = []
    base = {"type": "Any", "confidence": 0, "match": None}
    # clean up my_type
    my_type = return_text.strip().rstrip(".")
    my_type = my_type.replace("`", "")

    # print(my_type)
    if any(t in my_type for t in ("a list of", "list of", "an array")):
        # Lists of Any / Tuple
        lt = "Any"
        result = base.copy()
        result["confidence"] = 0.8  # OK
        for element in ("tuple", "string", "int"):
            if element in my_type:
                if element == "string":
                    lt = "str"
                else:
                    lt = element
                result["confidence"] = 0.9  # GOOD

        my_type = f"List[{lt}]"
        result["type"] = my_type
        candidates.append(result)

    if any(t in my_type for t in ("a dictionary", "dict")):
        # Lists of Any / Tuple
        lt = "Any"
        result = base.copy()
        result["confidence"] = 0.8  # OK
        if "tuple" in my_type:
            lt = "Tuple"
            result["confidence"] = 0.9  # GOOD
        my_type = f"Dict[{lt}]"
        result["type"] = my_type
        candidates.append(result)

    if any(t in my_type for t in ("tuple", "a pair")):
        result = base.copy()
        result["type"] = "Tuple"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(num in my_type for num in ("unsigned integer", "unsigned int", "unsigned")):
        # Assume unsigned are uint
        result = base.copy()
        result["type"] = "uint"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(
        num in my_type
        for num in (
            "number",
            "integer",
            "count",
            " int ",
            "length",
            "index",
            "**signed** value",
            "0 or 1",
            "nanoseconds",
        )
    ):
        # Assume numbers are signed int
        result = base.copy()
        result["type"] = "int"
        result["confidence"] = 0.7  # OK
        candidates.append(result)

    if any(t in my_type for t in (" number of ", "address of")):
        result = base.copy()
        result["type"] = "int"
        result["confidence"] = 0.85  # better match than bytes and bytearray
        candidates.append(result)

    if any(t in my_type for t in ("bytearray",)):
        result = base.copy()
        result["type"] = "bytearray"
        result["confidence"] = 0.83  # better match than bytes
        candidates.append(result)

    if any(t in my_type for t in ("bytes", "byte string")):
        result = base.copy()
        result["type"] = "bytes"
        result["confidence"] = 0.81  # OK, better than just string
        candidates.append(result)

    if any(t in my_type for t in ("boolean", "True", "False")):
        result = base.copy()
        result["type"] = "boolean"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(
        t in my_type
        for t in (
            "float",
            "logarithm",
            "sine",
            "tangent",
            "exponential",
            "complex number",
            "phase",
        )
    ):
        result = base.copy()
        result["type"] = "float"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("string",)):
        result = base.copy()
        result["type"] = "str"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("name", "names")):
        result = base.copy()
        result["type"] = "str"
        result["confidence"] = 0.3  # name could be a string
        candidates.append(result)

    if any(t in my_type for t in ("``None``", "None")):
        result = base.copy()
        result["type"] = "None"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("Object", "object")):
        words = my_type.split(" ")
        try:
            i = words.index("Object")
        except ValueError:
            try:
                i = words.index("object")
            except ValueError:
                # object is not a word, but is a part of a word
                i = 0

        if i > 0:
            object = words[i - 1]
            if object in ("stream-like", "file"):
                object = "stream"
            elif object == "callback":
                object = "Callable[..., Any]"
                # todo: requires additional 'from typing import Callable'

            # clean
            object = re.sub(r"[^a-z.A-Z0-9]", "", object)
            result = base.copy()
            result["type"] = object
            if object[0].isupper():
                result["confidence"] = 0.8  # Good
            else:
                result["confidence"] = 0.3  # not so good

            candidates.append(result)

    if " " in my_type:
        result = base.copy()
        result = {"type": "Any", "confidence": 0.2}
        candidates.append(result)
    elif my_type[0].isdigit() or len(my_type) < 3 or my_type in ("them", "the", "immediately"):
        # avoid short words, starts with digit, or a few detected
        result = base.copy()
        result = {"type": "Any", "confidence": 0.2}
        candidates.append(result)

    else:

        assert not " " in my_type
        assert not ":" in my_type
        result = base.copy()
        result["type"] = my_type
        result["confidence"] = 0.1  # medium
        candidates.append(result)
    return candidates


def type_from_docstring(docstring: Union[str, List[str]], signature: str, module: str):
    """Determine the return type of a function or method based on:
     - the function signature
     - the terminology used in the docstring

    Logic:
      - if the signature contains a return type --> <something> then that is returned
        - use re to find phrases such as:
            - 'Returns ..... '
            - 'Gets  ..... '
        - docstring is joined without newlines to simplify parsing
        - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
        - builds a list return type candidates
        - selects the highest ranking candidate
        - the default Type is 'Any'
    """

    if isinstance(docstring, list):
        # join with space to avoid ending at a newline
        docstring = " ".join(docstring)

    return_regex = r"Return(?:s?,?|(?:ing)?)\s(?!information)(?P<return>.*)[.|$|!|?]"
    gets_regex = r"Gets?\s(?P<return>.*)[.|$|\s]"

    #    function_regex = r"\w+(?=\()"
    # only the function name without the leading module
    function_re = re.compile(r"[\w|.]+(?=\()")

    matches: List[re.Match] = []
    candidates: List[Dict] = []

    # if the signature contains a return type , then use that and do nothing else.
    if "->" in signature:
        sig_type = signature.split("->")[-1].strip(": ")
        return {"type": sig_type, "confidence": 1, "match": signature}

    try:
        function_name = function_re.findall(signature)[0]
    except IndexError:
        function_name = signature.strip().strip(":()")

    function_name = ".".join((module, function_name))
    # lookup a few in the lookup list
    if function_name in LOOKUP_LIST.keys():
        sig_type = LOOKUP_LIST[function_name][0]
        return {
            "type": LOOKUP_LIST[function_name][0],
            "confidence": LOOKUP_LIST[function_name][1],
            "match": function_name,
        }

    for regex in (return_regex, gets_regex):
        match_iter = re.finditer(regex, docstring, re.MULTILINE | re.IGNORECASE)
        for match in match_iter:
            # matches.append(match)
            distilled = distill_return(match.group("return"))
            for item in distilled:
                candidate = {
                    "match": match,
                    "type": item["type"],
                    "confidence": item["confidence"],
                }
                candidates.append(candidate)
    # Sort
    # return the best candidate, or Any
    if len(candidates) > 0:
        candidates = sorted(candidates, key=lambda x: x["confidence"], reverse=True)
        # print(candidates[0])
        return candidates[0]  # best candidate
    else:
        return {"type": "Any", "confidence": 0, "match": None}
