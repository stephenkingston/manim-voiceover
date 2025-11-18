from manim import *

from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gemini import GeminiTTSService


class GeminiExample(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            GeminiTTSService(voice_name="Kore", model="gemini-2.5-flash-preview-tts")
        )

        circle = Circle()
        circle2 = Circle().shift(2 * LEFT)
        square = Square().shift(2 * RIGHT)

        with self.voiceover(text="""
            Say enthusiastically: இப்போ, 
            ரெண்டு வட்டம் <bookmark mark="drawcircles"/>,
            அப்பறோம் ஒரு சதுரம் <bookmark mark="drawsquare"/>, வரஞ்சுட்டோம்! 
        """) as tracker:
            self.play(FadeIn(circle))
            self.play(FadeIn(circle2))
            self.wait_until_bookmark("drawcircles")

            self.play(FadeIn(square))
            self.wait_until_bookmark("drawsquare")

        self.wait(1)
        # Remove everything
        self.play(FadeOut(circle), FadeOut(circle2), FadeOut(square))

        # English
        with self.voiceover(text="""
            Say enthusiastically: Now, two circles <bookmark mark="drawcircles"/>,
            and then a square <bookmark mark="drawsquare"/>,
            are drawn!
        """) as tracker:
            self.play(FadeIn(circle))
            self.play(FadeIn(circle2))
            self.wait_until_bookmark("drawcircles")

            self.play(FadeIn(square))
            self.wait_until_bookmark("drawsquare")

        self.wait(1)

        self.play(FadeOut(circle), FadeOut(circle2), FadeOut(square))

