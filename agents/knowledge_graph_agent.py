# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from typing import Any, Optional, Union

from unstructured.documents.elements import Element

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.prompts import TextPrompt
from camel.storages.graph_storages.graph_element import (
    GraphElement,
    Node,
    Relationship,
)
from camel.types import ModelType, RoleType

text_prompt = """
You are tasked with extracting nodes and relationships from given content and 
structures them into Node and Relationship objects. Here's the outline of what 
you needs to do:

Content Extraction:
You should be able to process input content and identify entities mentioned 
within it.
Entities can be any noun phrases or concepts that represent distinct entities 
in the context of the given content.

Node Extraction:
For each identified entity, you should create a Node object.
Each Node object should have a unique identifier (id) and a type (type).
Additional properties associated with the node can also be extracted and 
stored.

Relationship Extraction:
You should identify relationships between entities mentioned in the content.
For each relationship, create a Relationship object.
A Relationship object should have a subject (subj) and an object (obj) which 
are Node objects representing the entities involved in the relationship.
Each relationship should also have a type (type), and additional properties if 
applicable.

Output Formatting:
The extracted nodes and relationships should be formatted as instances of the 
provided Node and Relationship classes.
Ensure that the extracted data adheres to the structure defined by the classes.
Output the structured data in a format that can be easily validated against 
the provided code.

Instructions for you:
Read the provided content thoroughly.
Identify distinct entities mentioned in the content and categorize them as 
nodes.
Determine relationships between these entities and represent them as directed 
relationships.
Provide the extracted nodes and relationships in the specified format below.
Example for you:

Example Content:
"John works at XYZ Corporation. He is a software engineer. The company is 
located in New York City."

Expected Output:

Nodes:

Node(id='John', type='Person', properties={'agent_generated'})
Node(id='XYZ Corporation', type='Organization', properties={'agent_generated'})
Node(id='New York City', type='Location', properties={'agent_generated'})

Relationships:

Relationship(subj=Node(id='John', type='Person'), obj=Node(id='XYZ 
Corporation', type='Organization'), type='WorksAt', properties=
{'agent_generated'})
Relationship(subj=Node(id='John', type='Person'), obj=Node(id='New York City', 
type='Location'), type='ResidesIn', properties={'agent_generated'})

===== TASK =====
Please extracts nodes and relationships from given content and structures them 
into Node and Relationship objects. 

{task}
"""


class KnowledgeGraphAgent(ChatAgent):
    r"""An agent that can extract node and relationship information for
    different entities from given `Element` content.

    Attributes:
        task_prompt (TextPrompt): A prompt for the agent to extract node and
            relationship information for different entities.
    """

    def __init__(
        self,
        model_type: ModelType = ModelType.GPT_3_5_TURBO,
        model_config: Optional[Any] = None,
    ) -> None:
        r"""Initialize the `KnowledgeGraphAgent`.

        Args:
            model_type (ModelType, optional): The type of model to use for the
                agent. Defaults to `ModelType.GPT_3_5_TURBO`.
            model_config (Any, optional): The configuration for the model.
                Defaults to `None`.
        """
        system_message = BaseMessage(
            role_name="Graphify",
            role_type=RoleType.ASSISTANT,
            meta_dict=None,
            content="Your mission is to transform unstructured content "
            "intostructured graph data. Extract nodes and relationships with "
            "precision, and let the connections unfold. Your graphs will "
            "illuminate the hidden connections within the chaos of "
            "information.",
        )
        super().__init__(system_message, model_type, model_config)

    def run(
        self,
        element: Union[str, Element],
        parse_graph_elements: bool = False,
    ) -> Union[str, GraphElement]:
        r"""Run the agent to extract node and relationship information.

        Args:
            element (Union[str, Element]): The input element or string.
            parse_graph_elements (bool, optional): Whether to parse into
                `GraphElement`. Defaults to `False`.

        Returns:
            Union[str, GraphElement]: The extracted node and relationship
                information. If `parse_graph_elements` is `True` then return
                `GraphElement`, else return `str`.
        """
        self.reset()
        self.element = element

        knowledge_graph_prompt = TextPrompt(text_prompt)
        knowledge_graph_generation = knowledge_graph_prompt.format(
            task=str(element)
        )

        knowledge_graph_generation_msg = BaseMessage.make_user_message(
            role_name="Graphify", content=knowledge_graph_generation
        )

        response = self.step(input_message=knowledge_graph_generation_msg)

        content = response.msg.content

        if parse_graph_elements:
            content = self._parse_graph_elements(content)

        return content

    def _validate_node(self, node: Node) -> bool:
        r"""Validate if the object is a valid Node.

        Args:
            node (Node): Object to be validated.

        Returns:
            bool: True if the object is a valid Node, False otherwise.
        """
        return (
            isinstance(node, Node)
            and isinstance(node.id, (str, int))
            and isinstance(node.type, str)
        )

    def _validate_relationship(self, relationship: Relationship) -> bool:
        r"""Validate if the object is a valid Relationship.

        Args:
            relationship (Relationship): Object to be validated.

        Returns:
            bool: True if the object is a valid Relationship, False otherwise.
        """
        return (
            isinstance(relationship, Relationship)
            and self._validate_node(relationship.subj)
            and self._validate_node(relationship.obj)
            and isinstance(relationship.type, str)
        )

    def _parse_graph_elements(self, input_string: str) -> GraphElement:
        r"""Parses graph elements from given content.

        Args:
            input_string (str): The input content.

        Returns:
            GraphElement: The parsed graph elements.
        """
        import re

        # Regular expressions to extract nodes and relationships
        node_pattern = r"Node\(id='(.*?)', type='(.*?)', properties=(.*?)\)"
        rel_pattern = (
            r"Relationship\(subj=Node\(id='(.*?)', type='(.*?)'\), "
            r"obj=Node\(id='(.*?)', type='(.*?)'\), type='(.*?)', "
            r"properties=\{(.*?)\}\)"
        )

        nodes = {}
        relationships = []

        # Extract nodes
        for match in re.finditer(node_pattern, input_string):
            id, type, properties = match.groups()
            properties = eval(properties)
            if id not in nodes:
                node = Node(id, type, properties)
                if self._validate_node(node):
                    nodes[id] = node

        # Extract relationships
        for match in re.finditer(rel_pattern, input_string):
            subj_id, subj_type, obj_id, obj_type, rel_type, properties_str = (
                match.groups()
            )
            properties = eval(properties_str)
            if subj_id in nodes and obj_id in nodes:
                subj = nodes[subj_id]
                obj = nodes[obj_id]
                relationship = Relationship(subj, obj, rel_type, properties)
                if self._validate_relationship(relationship):
                    relationships.append(relationship)

        return GraphElement(list(nodes.values()), relationships, self.element)
