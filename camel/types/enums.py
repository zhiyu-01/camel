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
import re
from enum import Enum, EnumMeta


class RoleType(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    CRITIC = "critic"
    EMBODIMENT = "embodiment"
    DEFAULT = "default"


class ModelType(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"

    STUB = "stub"

    LLAMA_2 = "llama-2"
    LLAMA_3 = "llama-3"
    VICUNA = "vicuna"
    VICUNA_16K = "vicuna-16k"

    QWEN_2 = "qwen-2"
    GLM_4 = "glm-4"

    # Legacy anthropic models
    # NOTE: anthropic lagecy models only Claude 2.1 has system prompt support
    CLAUDE_2_1 = "claude-2.1"
    CLAUDE_2_0 = "claude-2.0"
    CLAUDE_INSTANT_1_2 = "claude-instant-1.2"

    #  3 models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    @property
    def value_for_tiktoken(self) -> str:
        return self.value if self is not ModelType.STUB else "gpt-3.5-turbo"

    @property
    def is_openai(self) -> bool:
        r"""Returns whether this type of models is an OpenAI-released model."""
        return self in {
            ModelType.GPT_3_5_TURBO,
            ModelType.GPT_4,
            ModelType.GPT_4_32K,
            ModelType.GPT_4_TURBO,
            ModelType.GPT_4O,
        }

    @property
    def is_open_source(self) -> bool:
        r"""Returns whether this type of models is open-source."""
        return self in {
            ModelType.LLAMA_2,
            ModelType.LLAMA_3,
            ModelType.VICUNA,
            ModelType.VICUNA_16K,
            ModelType.QWEN_2,
            ModelType.GLM_4,
        }

    @property
    def is_anthropic(self) -> bool:
        r"""Returns whether this type of models is Anthropic-released model.

        Returns:
            bool: Whether this type of models is anthropic.
        """
        return self in {
            ModelType.CLAUDE_INSTANT_1_2,
            ModelType.CLAUDE_2_0,
            ModelType.CLAUDE_2_1,
            ModelType.CLAUDE_3_OPUS,
            ModelType.CLAUDE_3_SONNET,
            ModelType.CLAUDE_3_HAIKU,
        }

    @property
    def token_limit(self) -> int:
        r"""Returns the maximum token limit for a given model.
        Returns:
            int: The maximum token limit for the given model.
        """
        if self is ModelType.GPT_3_5_TURBO:
            return 16385
        elif self is ModelType.GPT_4:
            return 8192
        elif self is ModelType.GPT_4_32K:
            return 32768
        elif self is ModelType.GPT_4_TURBO:
            return 128000
        elif self is ModelType.GPT_4O:
            return 128000
        elif self is ModelType.STUB:
            return 4096
        elif self is ModelType.LLAMA_2:
            return 4096
        elif self is ModelType.LLAMA_3:
            return 4096
        elif self is ModelType.QWEN_2:
            return 4096
        elif self is ModelType.GLM_4:
            return 4096
        elif self is ModelType.VICUNA:
            # reference: https://lmsys.org/blog/2023-03-30-vicuna/
            return 2048
        elif self is ModelType.VICUNA_16K:
            return 16384
        if self in {ModelType.CLAUDE_2_0, ModelType.CLAUDE_INSTANT_1_2}:
            return 100_000
        elif self in {
            ModelType.CLAUDE_2_1,
            ModelType.CLAUDE_3_OPUS,
            ModelType.CLAUDE_3_SONNET,
            ModelType.CLAUDE_3_HAIKU,
        }:
            return 200_000
        else:
            raise ValueError("Unknown model type")

    def validate_model_name(self, model_name: str) -> bool:
        r"""Checks whether the model type and the model name matches.

        Args:
            model_name (str): The name of the model, e.g. "vicuna-7b-v1.5".
        Returns:
            bool: Whether the model type mathches the model name.
        """
        if self is ModelType.VICUNA:
            pattern = r'^vicuna-\d+b-v\d+\.\d+$'
            return bool(re.match(pattern, model_name))
        elif self is ModelType.VICUNA_16K:
            pattern = r'^vicuna-\d+b-v\d+\.\d+-16k$'
            return bool(re.match(pattern, model_name))
        elif self is ModelType.LLAMA_2:
            return (
                self.value in model_name.lower()
                or "llama2" in model_name.lower()
            )
        elif self is ModelType.LLAMA_3:
            return (
                self.value in model_name.lower()
                or "llama3" in model_name.lower()
            )
        elif self is ModelType.QWEN_2:
            return (
                self.value in model_name.lower()
                or "qwen2" in model_name.lower()
            )
        elif self is ModelType.GLM_4:
            return (
                self.value in model_name.lower()
                or "glm4" in model_name.lower()
            )
        else:
            return self.value in model_name.lower()


class EmbeddingModelType(Enum):
    ADA_2 = "text-embedding-ada-002"
    ADA_1 = "text-embedding-ada-001"
    BABBAGE_1 = "text-embedding-babbage-001"
    CURIE_1 = "text-embedding-curie-001"
    DAVINCI_1 = "text-embedding-davinci-001"

    @property
    def is_openai(self) -> bool:
        r"""Returns whether this type of models is an OpenAI-released model."""
        return self in {
            EmbeddingModelType.ADA_2,
            EmbeddingModelType.ADA_1,
            EmbeddingModelType.BABBAGE_1,
            EmbeddingModelType.CURIE_1,
            EmbeddingModelType.DAVINCI_1,
        }

    @property
    def output_dim(self) -> int:
        if self is EmbeddingModelType.ADA_2:
            return 1536
        elif self is EmbeddingModelType.ADA_1:
            return 1024
        elif self is EmbeddingModelType.BABBAGE_1:
            return 2048
        elif self is EmbeddingModelType.CURIE_1:
            return 4096
        elif self is EmbeddingModelType.DAVINCI_1:
            return 12288
        else:
            raise ValueError(f"Unknown model type {self}.")


class TaskType(Enum):
    AI_SOCIETY = "ai_society"
    CODE = "code"
    MISALIGNMENT = "misalignment"
    TRANSLATION = "translation"
    EVALUATION = "evaluation"
    SOLUTION_EXTRACTION = "solution_extraction"
    ROLE_DESCRIPTION = "role_description"
    OBJECT_RECOGNITION = "object_recognition"
    DEFAULT = "default"
    DESCRIPTE_VIDEO = "descripte_video"


class VectorDistance(Enum):
    r"""Distance metrics used in a vector database."""

    DOT = "dot"
    r"""Dot product. https://en.wikipedia.org/wiki/Dot_product"""

    COSINE = "cosine"
    r"""Cosine similarity. https://en.wikipedia.org/wiki/Cosine_similarity"""

    EUCLIDEAN = "euclidean"
    r"""Euclidean distance. https://en.wikipedia.org/wiki/Euclidean_distance"""


class OpenAIBackendRole(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"
    FUNCTION = "function"


class TerminationMode(Enum):
    ANY = "any"
    ALL = "all"


class OpenAIImageTypeMeta(EnumMeta):
    def __contains__(cls, image_type: object) -> bool:
        try:
            cls(image_type)
        except ValueError:
            return False
        return True


class OpenAIImageType(Enum, metaclass=OpenAIImageTypeMeta):
    r"""Image types supported by OpenAI vision model."""

    # https://platform.openai.com/docs/guides/vision
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    WEBP = "webp"
    GIF = "gif"


class OpenAIVisionDetailType(Enum):
    AUTO = "auto"
    LOW = "low"
    HIGH = "high"


class StorageType(Enum):
    MILVUS = "milvus"
    QDRANT = "qdrant"


class OpenAPIName(Enum):
    COURSERA = "coursera"
    KLARNA = "klarna"
    SPEAK = "speak"
    NASA_APOD = "nasa_apod"
    BIZTOC = "biztoc"
    CREATE_QR_CODE = "create_qr_code"
    OUTSCHOOL = "outschool"
    WEB_SCRAPER = "web_scraper"


class AudioModelType(Enum):
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"

    @property
    def is_openai(self) -> bool:
        r"""Returns whether this type of audio models is an OpenAI-released
        model."""
        return self in {
            AudioModelType.TTS_1,
            AudioModelType.TTS_1_HD,
        }


class VoiceType(Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

    @property
    def is_openai(self) -> bool:
        r"""Returns whether this type of voice is an OpenAI-released voice."""
        return self in {
            VoiceType.ALLOY,
            VoiceType.ECHO,
            VoiceType.FABLE,
            VoiceType.ONYX,
            VoiceType.NOVA,
            VoiceType.SHIMMER,
        }
