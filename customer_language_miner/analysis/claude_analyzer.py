"""Claude-powered analyzer for customer language patterns."""

import anthropic
from typing import List, Dict, Any
import json


class ClaudeAnalyzer:
    """Analyzes customer language using Claude AI to identify patterns, pain points, and triggers."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze_batch(
        self,
        texts: List[str],
        context: str = "",
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Analyze a batch of customer texts for patterns and insights.

        Args:
            texts: List of customer texts to analyze
            context: Optional context about the product/category
            max_tokens: Maximum tokens for response

        Returns:
            Dictionary containing analysis results
        """
        prompt = self._build_analysis_prompt(texts, context)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            # Parse JSON response
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # If response isn't valid JSON, wrap it
                analysis = {"raw_analysis": response_text}

            return analysis

        except Exception as e:
            print(f"Error during Claude analysis: {str(e)}")
            return {"error": str(e)}

    def _build_analysis_prompt(self, texts: List[str], context: str) -> str:
        """Build the analysis prompt for Claude."""
        combined_texts = "\n\n---\n\n".join(texts[:100])  # Limit to 100 texts

        prompt = f"""You are an expert copywriter and customer research analyst. Analyze the following customer language samples to extract insights for advertising and marketing.

{"PRODUCT/CATEGORY CONTEXT: " + context if context else ""}

CUSTOMER LANGUAGE SAMPLES:
{combined_texts}

Please analyze these samples and provide a comprehensive JSON response with the following structure:

{{
  "emotional_patterns": [
    {{
      "emotion": "name of emotion (e.g., frustration, hope, fear, desire)",
      "frequency": "high/medium/low",
      "example_quotes": ["quote 1", "quote 2", "quote 3"],
      "trigger_words": ["word1", "word2"],
      "advertising_angle": "how to use this emotion in ads"
    }}
  ],
  "pain_points": [
    {{
      "pain_point": "description of the problem",
      "severity": "critical/major/minor",
      "frequency_mentioned": "percentage or count",
      "customer_quotes": ["quote 1", "quote 2"],
      "before_state": "how customers describe life before solution",
      "desired_outcome": "what they want instead"
    }}
  ],
  "desire_triggers": [
    {{
      "desire": "what customers want to achieve/become",
      "intensity": "high/medium/low",
      "language_patterns": ["pattern 1", "pattern 2"],
      "example_quotes": ["quote 1", "quote 2"],
      "aspirational_identity": "who they want to be"
    }}
  ],
  "awareness_stages": {{
    "unaware": {{
      "indicators": ["phrases that show no awareness of problem"],
      "quotes": ["example quotes"]
    }},
    "problem_aware": {{
      "indicators": ["phrases showing they know the problem"],
      "quotes": ["example quotes"]
    }},
    "solution_aware": {{
      "indicators": ["phrases showing they know solutions exist"],
      "quotes": ["example quotes"]
    }},
    "product_aware": {{
      "indicators": ["phrases showing they know specific products"],
      "quotes": ["example quotes"]
    }},
    "most_aware": {{
      "indicators": ["phrases from current/past customers"],
      "quotes": ["example quotes"]
    }}
  }},
  "language_patterns": {{
    "commonly_used_phrases": ["phrase 1", "phrase 2"],
    "metaphors_analogies": ["metaphor 1", "metaphor 2"],
    "objections": ["objection 1", "objection 2"],
    "questions_asked": ["question 1", "question 2"],
    "vocabulary_level": "simple/moderate/technical",
    "tone": "casual/professional/emotional"
  }},
  "key_insights": [
    "insight 1",
    "insight 2",
    "insight 3"
  ]
}}

Focus on extracting EXACT phrases and quotes that can be used directly in ad copy. Prioritize emotional, vivid language over generic descriptions."""

        return prompt

    def generate_ad_copy_framework(
        self,
        analysis: Dict[str, Any],
        max_tokens: int = 3000
    ) -> Dict[str, Any]:
        """
        Generate ad-ready hooks and body copy frameworks from analysis.

        Args:
            analysis: Analysis results from analyze_batch
            max_tokens: Maximum tokens for response

        Returns:
            Dictionary containing ad copy frameworks
        """
        prompt = f"""Based on the following customer language analysis, create ad-ready hooks and body copy frameworks.

ANALYSIS DATA:
{json.dumps(analysis, indent=2)}

Generate a JSON response with this structure:

{{
  "hooks": {{
    "problem_aware": [
      "Hook 1 using customer language",
      "Hook 2 using customer language",
      "Hook 3 using customer language"
    ],
    "solution_aware": [
      "Hook 1",
      "Hook 2",
      "Hook 3"
    ],
    "product_aware": [
      "Hook 1",
      "Hook 2",
      "Hook 3"
    ]
  }},
  "body_copy_frameworks": [
    {{
      "framework_name": "Problem-Agitate-Solution",
      "target_awareness": "problem_aware",
      "structure": {{
        "problem": "Using customer's exact language to describe problem",
        "agitate": "Making them feel the pain using their words",
        "solution": "Presenting solution in their language"
      }},
      "example": "Full example copy using customer quotes"
    }},
    {{
      "framework_name": "Before-After-Bridge",
      "target_awareness": "solution_aware",
      "structure": {{
        "before": "Customer's current state in their words",
        "after": "Desired outcome in their words",
        "bridge": "How to get there"
      }},
      "example": "Full example copy"
    }}
  ],
  "headline_formulas": [
    "Formula 1 with customer language",
    "Formula 2 with customer language"
  ],
  "call_to_action_suggestions": [
    "CTA 1 based on desires",
    "CTA 2 based on pain points"
  ],
  "objection_handlers": [
    {{
      "objection": "Common objection from analysis",
      "response": "How to handle it using customer language"
    }}
  ]
}}

Use EXACT customer quotes wherever possible. Make it ready to copy-paste into ads."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            try:
                ad_framework = json.loads(response_text)
            except json.JSONDecodeError:
                ad_framework = {"raw_framework": response_text}

            return ad_framework

        except Exception as e:
            print(f"Error generating ad copy framework: {str(e)}")
            return {"error": str(e)}

    def categorize_by_awareness(
        self,
        data: List[Dict],
        text_field: str = 'text'
    ) -> Dict[str, List[Dict]]:
        """
        Categorize customer texts by stage of awareness.

        Args:
            data: List of data items with text
            text_field: Field name containing the text

        Returns:
            Dictionary with awareness stages as keys
        """
        # Sample texts for batch processing
        texts = [item[text_field] for item in data if text_field in item][:50]

        if not texts:
            return {}

        prompt = f"""Categorize each of these customer texts by Eugene Schwartz's 5 stages of awareness:
1. Unaware - Don't know they have a problem
2. Problem Aware - Know the problem, not the solution
3. Solution Aware - Know solutions exist, not which one
4. Product Aware - Know about specific products/options
5. Most Aware - Ready to buy, just comparing

TEXTS TO CATEGORIZE:
{json.dumps(texts, indent=2)}

Respond with JSON:
{{
  "categorized": [
    {{
      "text_index": 0,
      "stage": "problem_aware",
      "confidence": "high/medium/low",
      "reasoning": "why this categorization"
    }}
  ]
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.2,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            result = json.loads(response_text)

            # Organize by stage
            categorized = {
                'unaware': [],
                'problem_aware': [],
                'solution_aware': [],
                'product_aware': [],
                'most_aware': []
            }

            for item in result.get('categorized', []):
                idx = item['text_index']
                stage = item['stage']
                if idx < len(data) and stage in categorized:
                    categorized[stage].append(data[idx])

            return categorized

        except Exception as e:
            print(f"Error categorizing by awareness: {str(e)}")
            return {}
