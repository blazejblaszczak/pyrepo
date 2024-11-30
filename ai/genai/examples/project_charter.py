import google.generativeai as genai
from Markdown2docx import Markdown2docx

"""
This code is used to automate the generation of a Project Charter document for a given product idea.
It uses Google’s generative AI model configured with certain parameters for text generation.
The generated text is then saved to a markdown file, which is converted and saved as a Word document.
"""

def generate(api_key, product_idea):
    
    genai.configure(api_key=api_key)
  
    prompt = f"""Act as a senior project manager with vast experience in software development. Write a brief Project Charter document for our product idea. The Project Charter should include the following sections: 
        1) Project Title and Description
        2) Project Purpose or Justification
        3) Objectives and Constraints
        4) Scope Description
        5) Project Deliverables
        6) Project Budget
        7) Stakeholder Identification
        8) High-Level Risks and Assumptions
        Our product idea is: {product_idea}
        Now please write the Project Charter with the 8 sections mentioned above: """
  
    response = genai.generate_text(prompt=prompt)
  
    # save as Word document
    with open("project_charter.md", "w") as file:
        file.write(response.result)
        file.close()
      
    md2docx = Markdown2docx("project_charter")
    md2docx.eat_soup()
    md2docx.save()
  
    return response.result
