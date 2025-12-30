from openai import OpenAI
import random
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class RoastGenerator:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        self.humor_styles = {
            'savage': {
                'intensity': 'brutal and merciless',
                'tone': 'sharp and cutting',
                'examples': 'like a professional roast comedian'
            },
            'playful': {
                'intensity': 'light and teasing',
                'tone': 'friendly but witty',
                'examples': 'like joking with a good friend'
            },
            'sarcastic': {
                'intensity': 'dry and clever',
                'tone': 'deadpan and ironic',
                'examples': 'like a sarcastic movie character'
            },
            'absurd': {
                'intensity': 'weird and unexpected',
                'tone': 'surreal but funny',
                'examples': 'like a comedy sketch'
            }
        }
    
    def generate_roast(self, photo_features: Dict, style: str = 'playful') -> str:
        """Generate a personalized roast based on photo analysis"""
        prompt = self._build_roast_prompt(photo_features, style)
        
        if not self.client:
            return self._fallback_roast(photo_features, style)
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a witty AI comedian specializing in photo roasts. Be creative and funny but never cruel or offensive."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            roast = response.choices[0].message.content.strip()
            return self._filter_content(roast)
            
        except Exception as e:
            return self._fallback_roast(photo_features, style)
    
    def generate_comeback(self, user_message: str, context: str = "") -> str:
        """Generate witty comeback to user input"""
        prompt = f"""
        User said: "{user_message}"
        Context: {context}
        
        Generate a witty, clever comeback that's funny but not mean-spirited.
        Keep it under 50 words.
        """
        
        if not self.client:
            return self._fallback_comeback()
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a quick-witted comedian. Generate clever comebacks that are funny but not hurtful."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._fallback_comeback()
    
    def create_standup_routine(self, photo_features: Dict, duration: str = "short") -> List[str]:
        """Create a mini stand-up routine based on photo"""
        jokes = []
        
        # Opening joke
        opening = self.generate_roast(photo_features, 'playful')
        jokes.append(f"So I was looking at this photo and... {opening}")
        
        # Middle jokes based on specific features
        if photo_features.get('faces', {}).get('count', 0) > 1:
            jokes.append("I see multiple people in this photo. Safety in numbers, smart choice!")
        
        if photo_features.get('objects', {}).get('glasses'):
            jokes.append("Those glasses are so thick, I bet you can see into next week!")
        
        # Closing joke
        closing = "But hey, at least you're brave enough to share photos online. That takes confidence... or poor judgment!"
        jokes.append(closing)
        
        return jokes[:3] if duration == "short" else jokes
    
    def _build_roast_prompt(self, features: Dict, style: str) -> str:
        """Build prompt for roast generation"""
        style_info = self.humor_styles.get(style, self.humor_styles['playful'])
        
        prompt = f"""
        Create a {style_info['intensity']} roast with a {style_info['tone']} tone, {style_info['examples']}.
        
        Photo analysis:
        - Faces detected: {features.get('faces', {}).get('count', 0)}
        - Face features: {features.get('faces', {}).get('features', [])}
        - Objects: {features.get('objects', {})}
        - Color theme: {features.get('colors', {}).get('theme', 'unknown')}
        - Image quality: {features.get('composition', {}).get('resolution', 'unknown')}
        
        Generate ONE witty roast (max 2 sentences) that's funny but not cruel.
        Focus on obvious visual elements that would be funny to comment on.
        """
        
        return prompt
    
    def _filter_content(self, roast: str) -> str:
        """Filter inappropriate content"""
        # Simple content filtering
        inappropriate_words = ['ugly', 'stupid', 'fat', 'dumb']
        filtered_roast = roast
        
        for word in inappropriate_words:
            if word.lower() in filtered_roast.lower():
                filtered_roast = filtered_roast.replace(word, "interesting")
        
        return filtered_roast
    
    def _fallback_roast(self, features: Dict, style: str) -> str:
        """Fallback roasts when API fails"""
        fallbacks = [
            "I'd roast you, but I'm afraid you'd melt from all that heat!",
            "This photo has more filters than a coffee shop!",
            "I've seen better composition in a toddler's finger painting!",
            "Is this a selfie or a witness protection photo?",
            "This photo screams 'I have a great personality'!"
        ]
        
        return random.choice(fallbacks)
    
    def _fallback_comeback(self) -> str:
        """Fallback comebacks when API fails"""
        comebacks = [
            "That's what they all say!",
            "I've heard better comebacks from a broken boomerang!",
            "Nice try, but I've seen sharper wit on a butter knife!",
            "Is that your final answer or are you still loading?"
        ]
        
        return random.choice(comebacks)