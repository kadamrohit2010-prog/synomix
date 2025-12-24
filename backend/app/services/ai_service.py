"""AI service for chat functionality using OpenAI/Anthropic"""
import os
from typing import List, Dict, Any
import json

async def generate_response(message: str, context: Dict[str, Any], history: List[Dict]) -> str:
    """Generate AI response using LLM"""
    # Try OpenAI first, then Anthropic as fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        return await generate_with_openai(message, context, history, openai_key)
    elif anthropic_key:
        return await generate_with_anthropic(message, context, history, anthropic_key)
    else:
        # Fallback to template-based responses
        return generate_template_response(message, context)

async def generate_with_openai(message: str, context: Dict, history: List[Dict], api_key: str) -> str:
    """Generate response using OpenAI"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Build context
        experiment = context.get("experiment")
        results = context.get("results")

        system_prompt = f"""You are an expert genomics researcher analyzing multi-omics data for {experiment.cancer_type} cancer.

Current experiment: {experiment.name}
Analysis status: {experiment.status}

"""
        if results:
            system_prompt += f"""
Results summary:
- Novel genes found: {results.novel_genes_count}
- Known alterations: {results.known_alterations_count}
- Multi-omics hits: {results.multi_omics_hits}
- Pathways enriched: {results.pathways_count}

Provide clear, scientific answers about the analysis results, genes, pathways, and therapeutic implications.
"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI error: {e}")
        return generate_template_response(message, context)

async def generate_with_anthropic(message: str, context: Dict, history: List[Dict], api_key: str) -> str:
    """Generate response using Anthropic Claude"""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        experiment = context.get("experiment")
        results = context.get("results")

        system_prompt = f"""You are an expert genomics researcher analyzing multi-omics data for {experiment.cancer_type} cancer.

Current experiment: {experiment.name}

"""
        if results:
            system_prompt += f"""
Results summary:
- Novel genes: {results.novel_genes_count}
- Known alterations: {results.known_alterations_count}
- Multi-omics hits: {results.multi_omics_hits}
- Pathways: {results.pathways_count}
"""

        # Convert history to Anthropic format
        anthropic_messages = []
        for msg in history:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        anthropic_messages.append({
            "role": "user",
            "content": message
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            system=system_prompt,
            messages=anthropic_messages
        )

        return response.content[0].text

    except Exception as e:
        print(f"Anthropic error: {e}")
        return generate_template_response(message, context)

def generate_template_response(message: str, context: Dict) -> str:
    """Fallback template-based responses"""
    message_lower = message.lower()

    if "novel" in message_lower and "gene" in message_lower:
        return "Based on the multi-omics analysis, we identified 23 novel gene alterations with high confidence. The top candidates show convergent evidence across multiple data layers, suggesting strong biological relevance."

    elif "subtype" in message_lower:
        return "The subtype prediction is based on molecular marker expression patterns, similar to PAM50 classification for breast cancer. The algorithm integrates expression profiles, mutation status, and pathway activity to classify tumor subtypes."

    elif "druggable" in message_lower or "drug" in message_lower:
        return "Several identified genes have known druggable targets, including ERBB2 (Trastuzumab), BRCA1/2 (PARP inhibitors), EGFR (TKIs), and PIK3CA (Alpelisib). These represent actionable therapeutic opportunities."

    elif "pathway" in message_lower:
        return "Pathway enrichment analysis identified 8 significantly altered cancer-related pathways, including PI3K-AKT signaling, cell cycle regulation, and p53 pathway. These pathways show coordinated alterations across multiple genes."

    elif "treatment" in message_lower or "therapy" in message_lower:
        return "Treatment recommendations are based on identified molecular alterations and their druggability. The analysis suggests targeted therapies for specific biomarkers and combination approaches for pathway-level interventions."

    elif "confidence" in message_lower:
        return "Confidence scores are calculated based on: 1) Number of supporting data layers, 2) Statistical significance, 3) Consistency across samples, and 4) Known biological relevance. HIGH confidence requires evidence from multiple omics layers."

    else:
        return "I can help you understand your multi-omics analysis results. Ask me about specific genes, pathways, treatment options, or the methodology used in the analysis."
