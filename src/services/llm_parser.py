"""LLM-based message parser using Google Gemini and Langchain."""

import logging
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.config import settings

logger = logging.getLogger(__name__)


class TShirtRequest(BaseModel):
    """Structured output for t-shirt requests."""

    phrase: str = Field(description="The main phrase/text to put on the t-shirt")
    style: str = Field(
        description="The text style (e.g., bold, script, modern, retro, graffiti)"
    )
    wants_image: bool = Field(
        description="Whether the user wants an accompanying image/graphic"
    )
    image_description: Optional[str] = Field(
        default=None,
        description="Description of the image to generate, if requested",
    )
    color_preference: Optional[str] = Field(
        default=None,
        description="Preferred t-shirt or design color, if mentioned",
    )


class LLMParser:
    """Parser for extracting t-shirt request details from messages using Gemini."""

    def __init__(self):
        """Initialize the LLM parser with Gemini."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.google_api_key,
            temperature=0.7,
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=TShirtRequest)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that extracts t-shirt design requests from user messages.
Your job is to identify:
1. The main phrase/text the user wants on their t-shirt
2. The style of text they want (infer from context if not explicit)
3. Whether they want any images or graphics
4. What kind of image (if mentioned)
5. Color preferences (if any)

Be creative in interpreting the user's intent. If they say something like "I need a shirt that says 'Coffee is life'",
extract "Coffee is life" as the phrase.

{format_instructions}"""),
            ("user", "{message}"),
        ])

    async def parse_message(self, message: str) -> Optional[TShirtRequest]:
        """
        Parse a message to extract t-shirt request details.

        Args:
            message: The user's message

        Returns:
            TShirtRequest object with extracted details, or None if parsing fails
        """
        try:
            logger.info(f"Parsing message with Gemini: {message[:100]}...")
            
            chain = self.prompt | self.llm
            
            response = await chain.ainvoke({
                "message": message,
                "format_instructions": self.output_parser.get_format_instructions(),
            })
            
            # Parse the response
            parsed = self.output_parser.parse(response.content)
            
            logger.info(
                f"Successfully parsed request - Phrase: '{parsed.phrase}', "
                f"Style: {parsed.style}, Wants image: {parsed.wants_image}"
            )
            
            return parsed

        except Exception as e:
            logger.error(f"Error parsing message: {e}", exc_info=True)
            
            # Fallback: simple extraction
            return self._fallback_parse(message)

    def _fallback_parse(self, message: str) -> TShirtRequest:
        """
        Fallback parser when LLM fails.

        Args:
            message: The user's message

        Returns:
            Basic TShirtRequest object
        """
        logger.warning("Using fallback parser")
        
        # Simple extraction - just use the message as the phrase
        # Remove common trigger words
        phrase = message
        for keyword in settings.trigger_keywords_list:
            phrase = phrase.replace(keyword, "").strip()
        
        # Clean up common phrases
        for prefix in ["that says", "with", "saying", "i want a", "make me a"]:
            if prefix in phrase.lower():
                parts = phrase.lower().split(prefix)
                if len(parts) > 1:
                    phrase = parts[1].strip()
        
        # Remove quotes if present
        phrase = phrase.strip('"\'')
        
        return TShirtRequest(
            phrase=phrase or "Custom T-Shirt",
            style="modern",
            wants_image=False,
            image_description=None,
            color_preference=None,
        )
