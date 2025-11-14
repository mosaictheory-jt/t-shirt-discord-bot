"""T-shirt design image generator using PIL and optional AI image generation."""

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.services.llm_parser import TShirtRequest

logger = logging.getLogger(__name__)


class DesignGenerator:
    """Generates t-shirt design images with text and optional graphics."""

    def __init__(self):
        """Initialize the design generator."""
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Standard t-shirt design dimensions (for Printful)
        self.design_width = 4500
        self.design_height = 5400

    async def generate_design(
        self,
        request: TShirtRequest,
    ) -> Tuple[Path, bytes]:
        """
        Generate a t-shirt design based on the request.

        Args:
            request: The parsed t-shirt request

        Returns:
            Tuple of (file_path, image_bytes)
        """
        logger.info(f"Generating design for phrase: '{request.phrase}'")

        try:
            # Create the design image
            image = self._create_text_design(
                text=request.phrase,
                style=request.style,
                color_preference=request.color_preference,
            )

            # TODO: Add AI-generated image if requested
            # if request.wants_image and request.image_description:
            #     image = await self._add_ai_generated_image(
            #         image, request.image_description
            #     )

            # Save the image
            file_path = self.output_dir / f"design_{hash(request.phrase)}.png"
            image.save(file_path, "PNG")
            
            # Also get bytes for upload
            buffer = BytesIO()
            image.save(buffer, "PNG")
            image_bytes = buffer.getvalue()

            logger.info(f"Design saved to {file_path}")
            return file_path, image_bytes

        except Exception as e:
            logger.error(f"Error generating design: {e}", exc_info=True)
            raise

    def _create_text_design(
        self,
        text: str,
        style: str,
        color_preference: Optional[str] = None,
    ) -> Image.Image:
        """
        Create a text-based design.

        Args:
            text: The text to render
            style: The style to apply
            color_preference: Optional color preference

        Returns:
            PIL Image with the design
        """
        # Create a transparent image
        image = Image.new("RGBA", (self.design_width, self.design_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Determine text color based on preference
        text_color = self._get_text_color(color_preference)

        # Try to load a nice font, fall back to default
        font = self._get_font(style, text)

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.design_width - text_width) // 2
        y = (self.design_height - text_height) // 2

        # Draw text with outline for better visibility
        outline_color = self._get_outline_color(text_color)
        outline_width = 3
        
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=text_color)

        # Apply style-specific effects
        if style.lower() in ["retro", "vintage"]:
            image = self._apply_retro_effect(image)
        elif style.lower() in ["graffiti", "street"]:
            # Could add graffiti-style effects
            pass

        return image

    def _get_font(self, style: str, text: str) -> ImageFont.FreeTypeFont:
        """
        Get an appropriate font for the style.

        Args:
            style: The text style
            text: The text (to calculate size)

        Returns:
            PIL Font object
        """
        # Calculate font size based on text length
        base_size = 400
        text_length = len(text)
        
        if text_length > 50:
            font_size = 200
        elif text_length > 30:
            font_size = 300
        elif text_length > 15:
            font_size = 350
        else:
            font_size = base_size

        # Try to use system fonts
        try:
            # Common font paths on different systems
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\arial.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, font_size)
            
            # If no font found, use default
            logger.warning("Could not find system font, using default")
            return ImageFont.load_default()

        except Exception as e:
            logger.warning(f"Error loading font: {e}, using default")
            return ImageFont.load_default()

    def _get_text_color(self, color_preference: Optional[str]) -> Tuple[int, int, int, int]:
        """
        Get text color based on preference.

        Args:
            color_preference: Optional color preference

        Returns:
            RGBA color tuple
        """
        if color_preference:
            color_lower = color_preference.lower()
            color_map = {
                "red": (255, 0, 0, 255),
                "blue": (0, 0, 255, 255),
                "green": (0, 255, 0, 255),
                "yellow": (255, 255, 0, 255),
                "purple": (128, 0, 128, 255),
                "orange": (255, 165, 0, 255),
                "pink": (255, 192, 203, 255),
                "white": (255, 255, 255, 255),
                "black": (0, 0, 0, 255),
            }
            
            for color_name, rgba in color_map.items():
                if color_name in color_lower:
                    return rgba
        
        # Default to black
        return (0, 0, 0, 255)

    def _get_outline_color(
        self,
        text_color: Tuple[int, int, int, int],
    ) -> Tuple[int, int, int, int]:
        """
        Get outline color (contrasting with text color).

        Args:
            text_color: The main text color

        Returns:
            RGBA color tuple for outline
        """
        # If text is dark, use white outline; if light, use black
        brightness = (text_color[0] + text_color[1] + text_color[2]) / 3
        
        if brightness > 128:
            return (0, 0, 0, 255)  # Black outline for light text
        else:
            return (255, 255, 255, 255)  # White outline for dark text

    def _apply_retro_effect(self, image: Image.Image) -> Image.Image:
        """
        Apply a retro/vintage effect to the image.

        Args:
            image: The input image

        Returns:
            Image with retro effect applied
        """
        # Simple retro effect: slightly reduce color saturation
        # This is a placeholder for more complex effects
        return image
