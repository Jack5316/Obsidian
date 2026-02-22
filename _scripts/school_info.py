"""School Information Skill - Discover interesting facts about your alma maters.

This skill fetches and shares fascinating information about Xi'an Jiaotong-Liverpool University (XJTLU)
and University College London (UCL), including history, notable alumni, achievements, and current news.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


# School data with curated information
SCHOOL_DATA = {
    "xjtlu": {
        "name": "Xi'an Jiaotong-Liverpool University",
        "chinese_name": "西交利物浦大学",
        "founded": 2006,
        "location": "Suzhou, China",
        "partners": ["Xi'an Jiaotong University", "University of Liverpool"],
        "description": "An international university with a focus on global education",
        "notable_facts": [
            "First Sino-British university with independent legal entity status in China",
            "Campus designed by renowned British architects Gensler",
            "Known for its strong engineering and computer science programs",
            "Offers dual degrees from both Xi'an Jiaotong University and University of Liverpool",
            "Main teaching language is English"
        ],
        "notable_alumni": [
            "Graduates have pursued advanced degrees at top universities including Oxford, Cambridge, MIT",
            "Many alumni work at Fortune 500 companies in tech, finance, and consulting"
        ],
        "achievements": [
            "Ranked among the top international universities in China",
            "Strong research output in artificial intelligence and data science",
            "Modern campus with state-of-the-art research facilities"
        ],
        "interesting_trivia": [
            "XJTLU's campus features a stunning architectural design blending Eastern and Western elements",
            "The university has a unique '2+2' and '4+X' program structure",
            "Home to numerous international students from over 50 countries"
        ]
    },
    "ucl": {
        "name": "University College London",
        "founded": 1826,
        "location": "London, United Kingdom",
        "partners": ["Part of the University of London", "Russell Group"],
        "description": "London's leading multidisciplinary university",
        "notable_facts": [
            "The first university in England to admit students regardless of their religion",
            "The first university in England to admit women on equal terms with men",
            "Ranked among the top 10 universities globally in various rankings",
            "Located in the heart of London in Bloomsbury",
            "Part of the prestigious Russell Group of research-intensive universities"
        ],
        "notable_alumni": [
            "Mahatma Gandhi - Leader of Indian independence movement",
            "Alexander Graham Bell - Inventor of the telephone",
            "Peter Higgs - Nobel Prize in Physics (2013) for Higgs boson",
            "Francis Crick - Co-discoverer of DNA structure",
            "Christopher Nolan - Acclaimed film director",
            "Ricky Gervais - Comedian and actor",
            "Coldplay - Internationally renowned band (members met at UCL)",
            "George Orwell - Author (Eton but briefly attended UCL)",
            "Marie Stopes - British palaeobotanist and birth control pioneer",
            "John Stuart Mill - Philosopher and MP"
        ],
        "achievements": [
            "30 Nobel Prize winners among alumni and staff",
            "3 Field Medalists",
            "Pioneering research in numerous fields including medicine, physics, and social sciences",
            "One of the largest universities in the UK by student population",
            "Strong focus on interdisciplinary research"
        ],
        "interesting_trivia": [
            "UCL's main building has a statue of philosopher Jeremy Bentham (though it's actually his auto-icon - skeleton with wax head)",
            "The university's motto is 'Cuncti adsint meritaeque consortia virtutis' (Let all come who are worthy and seek virtue)",
            "UCL has a strong connection to the discovery of noble gases",
            "The Petrie Museum of Egyptian Archaeology at UCL contains one of the world's largest collections of Egyptian artifacts",
            "UCL was the first university in England to found a student union",
            "The famous Grant Museum of Zoology at UCL contains rare specimens including a quagga and a dodo"
        ],
        "fun_facts": [
            "The band Coldplay formed at UCL in 1996 when Chris Martin met Jonny Buckland during orientation week",
            "UCL's Bloomsbury campus has been featured in numerous films including 'Inception', 'The Dark Knight', and 'Sherlock Holmes'",
            "The Jeremy Bentham auto-icon sits in the UCL Student Centre and is occasionally brought to meetings (though he doesn't vote)",
            "UCL has its own university mace dating back to 1838, made of solid silver and decorated with precious stones"
        ]
    }
}


SCHOOL_PROMPT = """You are a university historian and public relations expert with deep knowledge 
of prestigious universities worldwide. Your task is to create an engaging, informative, and 
well-structured summary of interesting facts about the university described below.

Focus on:
1. Most surprising and fascinating facts
2. Notable achievements and alumni
3. Unique traditions and characteristics
4. Connections to world events or cultural impact
5. Fun and engaging trivia that makes the university special

Make the tone conversational but informative. Use bullet points for readability.
Highlight what makes this university special and worthy of pride for its alumni.

Structure the output with clear sections:
- Quick Facts
- What Makes It Special
- Famous & Impressive Alumni
- Amazing Achievements
- Fun Trivia & Hidden Gems
- A Moment of Pride

End with a reflection on why being an alumnus of this university is something to be proud of.

Use markdown for formatting. Make it engaging and celebratory!"""


def generate_school_content(school_key: str) -> str:
    """Generate engaging content about a school."""
    school = SCHOOL_DATA.get(school_key, {})
    if not school:
        return f"Unknown school: {school_key}"
    
    # Prepare content for AI enhancement
    content = f"""
University: {school['name']}
Founded: {school['founded']}
Location: {school['location']}

Notable Facts:
{chr(10).join('- ' + fact for fact in school['notable_facts'])}

Notable Alumni:
{chr(10).join('- ' + alum for alum in school['notable_alumni'])}

Achievements:
{chr(10).join('- ' + ach for ach in school['achievements'])}

Interesting Trivia:
{chr(10).join('- ' + trivia for trivia in school['interesting_trivia'])}

{'Fun Facts:' + chr(10) + chr(10).join('- ' + fact for fact in school['fun_facts']) if 'fun_facts' in school else ''}
"""
    
    # Get AI-enhanced content
    enhanced_content = summarize(content, SCHOOL_PROMPT)
    
    return enhanced_content


def main():
    """Main function for the school info skill."""
    parser = argparse.ArgumentParser(
        description="School Information Skill - Discover interesting facts about your alma maters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill school                    # Show info about both schools
  /skill school --school xjtlu    # Show info about XJTLU only
  /skill school --school ucl       # Show info about UCL only
  /skill school --save             # Save output to vault
"""
    )
    
    parser.add_argument(
        "--school",
        type=str,
        choices=["xjtlu", "ucl", "both"],
        default="both",
        help="Which school to show (xjtlu, ucl, or both)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault"
    )
    
    args = parser.parse_args()
    
    # Generate content
    output_parts = []
    output_parts.append("# School Pride - Your Alma Maters\n")
    output_parts.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n")
    output_parts.append("---\n")
    
    if args.school in ["both", "xjtlu"]:
        output_parts.append("\n## Xi'an Jiaotong-Liverpool University (XJTLU)\n")
        output_parts.append(generate_school_content("xjtlu"))
        output_parts.append("\n---\n")
    
    if args.school in ["both", "ucl"]:
        output_parts.append("\n## University College London (UCL)\n")
        output_parts.append(generate_school_content("ucl"))
    
    full_output = "\n".join(output_parts)
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/School Pride - {date_str}.md", full_output)
    
    print(full_output)


if __name__ == "__main__":
    main()
