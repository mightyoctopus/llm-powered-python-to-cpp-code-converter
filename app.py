import os, io, sys, subprocess
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import gradio as gr
from datetime import datetime
from placeholder_python_code import pi_1, pi_2
from css_elements import css_elements

### Environment
load_dotenv(".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

### Initialize
openai_client = OpenAI(api_key=OPENAI_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
OPENAI_MODEL = "gpt-5-mini-2025-08-07"
GEMINI_MODEL = "gemini-1.5-flash"


system_message = """
    You are an assistant that reimplements Python code in high performance C++
    for an M1 Mac.
""".strip()

system_message += """
    Respond only with C++; use comments sparingly and do not provide any
    explanation other than occasion comments.
""".strip()

system_message += """
    The C++ response needs to produce an identical output in the 
    fastest possible time. 
""".strip()

current_time = datetime.now().strftime("%Y%m%d_%H:%M:%S")

def user_prompt_for_python(python_code):
    user_prompt = """
        Rewrite this Python code in C++ with the fastest possible implementation
        that produces identical output in the least time.
    """.strip()
    user_prompt += """
        Respond only with C++ code; do not explain your work other than the real code. 
        And also do not include ```cpp and as such. But just working code only!
    """.strip()
    user_prompt += """
        Pay attention to number types to ensure no int overflows. Remember to #include 
        all necessary C++ packages such as iomanip.\n\n
    """.strip()
    user_prompt += python_code

    return user_prompt

def messages_for_python(python):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for_python(python)}
    ]

### remove ```cpp and ```
### cpp is a file extension of C++ code
def write_output(cpp: str):
    code = cpp.replace("```cpp", "").replace("```", "")
    with open(f"optimized-{current_time}.cpp", "w") as f:
        f.write(code)

def convert_and_optimize_code_with_openai(python):
    stream = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages_for_python(python),
        stream=True
    )
    stream_response = ""
    for chunk in stream:
        fragment = chunk.choices[0].delta.content or ""
        stream_response += fragment
        # print(fragment, end="", flush=True)

        yield fragment

def convert_and_optimize_code_with_gemini(python):
    user_prompt = user_prompt_for_python(python)

    stream = gemini_client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=user_prompt
    )

    for chunk in stream:
        stream_response = getattr(chunk, "text", None)
        if stream_response:
            yield stream_response

    ### OR THIS -- Gemini model returns an object other than string. So it needs to retrieve the text
    # for chunk in stream:
    #     if chunk.text:
    #         yield chunk.text


# convert_and_optimize_code_with_openai(pi_1)


###============================= GRADIO UI ================================###

def stream_text_on_ui(model, pi):
    """
    :param model: The selected LLM model used for converting Python code to C++
    :param pi: Input Python code string
    :yield response: Each chunk of stream data(generated text) received from LLM call
    """
    response = ""
    if model == "GPT-5":
        stream_res = convert_and_optimize_code_with_openai(pi)
    elif model == "Gemini":
        stream_res = convert_and_optimize_code_with_gemini(pi)
    else:
        raise ValueError("Unknown model...")
    ### another loop to take in the streaming chunk
    for chunk in stream_res:
        response += chunk
        response = response.replace("```cpp", "").replace("```", "").replace("cpp", "")
        yield response

def run_python_code(code: str):
    output = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = output
        ### For proper ISOLATION: use a fresh globals __main__ dict
        exec(code, {"__name__": "__main__"})
        return output.getvalue()
    except Exception as e:
        return output.getvalue() + f"-- {e}"
    finally:
        sys.stdout = old_stdout

### subprocess used to connect to the external programs (g++ for c++ build and compile)
def run_cpp_code(code: str):
    write_output(code)
    try:
        ### 1. Compile the code
        compile_cmd = [
            "clang++", "-Ofast", "-std=c++17",
            "-march=armv8.5-a", "-mtune=apple-m1",
            "-mcpu=apple-m1", "-o", "optimized",
            f"optimized-{current_time}.cpp"
        ]
        subprocess.run(
            compile_cmd, check=True, text=True, capture_output=True
        )

        ### 2. Run the code
        run_cmd = [f"./optimized"]
        run_result = subprocess.run(
            run_cmd, check=True, text=True, capture_output=True
        )
        return run_result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred:\n{e.stderr}"


with gr.Blocks(
    css=css_elements,
    title="Python To C++ Code Convertor"
) as ui:
    with gr.Row():
        pi_textbox = gr.Textbox(label="Place Python Code Here:", lines=20, value=pi_1)
        cpp_output = gr.Textbox(label="C++ Code Converted:", lines=20)

    with gr.Row():
        model_selection = gr.Dropdown(
            choices=["GPT-5", "Gemini"],
            label="Select Model",
            value="GPT-5",
            interactive=True
        )

    with gr.Row():
        convert_btn = gr.Button(value="Convert", size="lg")

    with gr.Row():
        run_py_btn = gr.Button(value="Run Python")
        run_cpp_btn = gr.Button(value="Run C++")

    with gr.Row():
        python_out = gr.TextArea(label="Python Result:", elem_classes=["python"])
        cpp_out = gr.TextArea(label="C++ Result:", elem_classes=["cpp"])

    convert_btn.click(
        fn=stream_text_on_ui,
        inputs=[model_selection, pi_textbox],
        outputs=cpp_output
    )

    run_py_btn.click(
        fn=run_python_code,
        inputs=pi_textbox,
        outputs=python_out
    )
    run_cpp_btn.click(
        fn=run_cpp_code,
        inputs=cpp_output,
        outputs=cpp_out
    )


ui.launch(inbrowser=True, share=True)



















