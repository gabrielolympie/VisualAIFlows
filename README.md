# VisualAIFlows
A simple Fast API Backend for Ironclad/rivet, enabling easily create python components, and orchestrate them with rivet

![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/5d04deb9-84f4-492c-9fba-407cc58cd3bb)

# Release Note PreAlpha
As of today this repo enables:
- Creation of python function, and implementation of rivet subgraphs that call these function through a http request to fast API
- Easy to use helper to update a rivet project based on this
- A playground that automatically load all the subgraphs created to ease their usage

Currently implemented routes:
- load_hf_hosted_model: a route to load a model that is hosted on huggingface (works with free tier model like mixtral)
- load_ollama_model: a route to pre load a model with ollama (great for local models)
- load_whisper: a route to load a whisper model with faster_whisper
- run_prompt: a route to run a prompt with a loaded model (streaming is still work in progress for this one)
- transcribe: a route to load an audio file and transcribe it to text (streaming is still work in progress for this one)
- run_code_with_error: a route to execute some string written python code and return either the console output or the error if it fails (still experimental)

# How to use
## Installation
- Clone this repo
- Install the requirements
- Move into VisualAIFlows/visualflows

- Optional: Install ollama: curl https://ollama.ai/install.sh | sh

## Basic Usage: Plug and play in rivet
#### Update the presets
- the auth.yaml allows you to add some api keys to the playground if you require some
- the models/presets/ollama_llm_presets.yaml and models/presets/hf_open_llm_presets.yaml enables you to update the ollama and huggingface hosted models you already have access to

#### Update the project
run the command: python backend.py
This will get all presets and methods, and update the project and playground with them. It will also export a standalone version of the subgraphs in the /components folder if you want to use them in an other rivet project

#### Start the backend
run the command: uvicorn backend:app --reload
There will be streaming printed in this invite

#### You are good to go, you can start rivet and load the visual flows project as any other rivet project (base project also contains an hello world)

# Vision, behind the scene and limitations
## Vision
Visual interface can be very powerfull to develop some piece of code, even though it can quickly get cluttered, and currently existing solution are either very class oriented and specialized on chatbots (like langflow/langchain) or javascript only (flowise.ai and ironclad/rivet). Based on this I wanted to create the best of both worlds, with a solution capable of leveraging a powerful and function oriented framework like rivet, with a versatile and powerfull backend like python.

My end goal for this poject will be to visualize and monitor complex flows in a very visual manner, with the possibility to watch the output at every step. Hence the main functions won't be focused on agents like in langchain, but rather on flows, as described in this repository : https://github.com/epfl-dlab/aiflows

## Behind the scenes & Advanced Usage
Behind the scene, this repo is doing several operation when used.

#### Fast Api serving
Basically, backend is a fastapi one and could be easily updated with existing projects like https://github.com/Dicklesworthstone/swiss_army_llama
All the python methods are hence served through http post and get request and leverage the http component from rivet to do that

#### Graph building
The main add-on of this repo is to enable the construction of input-output subgraph that will tremendously ease the usage of the backend, by prebuilding the graphs with default parameters and structured outputs.

#### The framework
##### Presets
Presets are default parameters you want to easily use in the project, you can edit them and add them in the models/presets directory.
Presets are yaml files with the following structure:
graph_description: A string description of what the graph does
graph_id: a unique id used to identify the preset inside the project. This id is hardcoded to enable backward compatibility in new projects, so don't forget to update that for new presets or it will break the project because of id duplication
graph_name: the name of the graph, that will be used in the project, ex : presets/auth_presets
values: a dictionnary of key: values items. The key will be used as named in the project to return the values
values_type: either string or number, all values should be of the same type

When the yaml is created, you can add it to the backend.py file, in the presets list, then run python backend.py to update the project
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/ec033b43-0f10-48de-b288-c945b5fa2fcb)

##### Methods
Methods are input output components that call a fastapi route, and return the outputs. They are based both on the libs and models/methods folders

In the libs you can add your helpers, functions and class.
Then you can define your method in a yaml in the models/methods
The function should be based on a pydantic method and a python function using this model as an input

graph_description: A string description of what the graph does
graph_id: a unique id used to identify the graph inside the project. This id is hardcoded to enable backward compatibility in new projects, so don't forget to update that for new presets or it will break the project because of id duplication
graph_name: the name of the graph, that will be used in the project, ex : methods/run_code_with_error 
fast_api_route: the route to access the method in fast api
inputs: a dictionnary of key: inputinfo, with input info being a dict {type: str or int, data_type: number or string, value: the default value for the method}
outputs: a dictionnary of key:types, with key being the name of the input, and type either string or number (multi output is not yet supported, but WIP)

Once the yaml and the functions are created, go into backend.py, add the function import, and add it in the methods dict (name:function)

![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/a1c3a010-7f9a-4c00-b5da-70bd5885ffc7)

##### Flows
WIP

##### State
A very basic state is implemented to be able to load objects in the backend and reuse them later in rivet. So far it is just a global dict implemented that can be accessed from any function in the project through the methods read_state, write_state and get_state.

You can check the libs/speech_recognition.py for an example usage.

The state is used in the visual interface with the identifier field, that select what object from the state is used

#### Helpers
You may notice that the ollama_llm_presets.yaml have a different format than other ones. Indeed it also have a downloads field.
This can be used with the gguf_to_ollama.py helper that is inside the downloads folder, that will download gguf models from huggingface, and push them to your local ollama integration.

The download for ollama is in shape name:url
The name is used to create the ollama model name, so it should be the same as the values of the values, and should not contain '_' caracters (that seems to not work well with ollama)

#### Playground
When running the python backend.py command, it will do the following:
- load the project named in the backend.py file
- Remove all graph that contain "name: presets/", "name: methods/","name: flows/","name: Playground:"
- Recreate them from your models yaml and function
- Create a playground with all methods and element already loaded, so that you can just duplicate them and use them easily/

As the parsing is name based, it is strongly advised to not use any of the key names in your project, to avoid accidental override
The update is still experimental and subject to failure and potential overrite, so i suggest to export your important graph separately

# Examples:
The playground:
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/3303b418-1572-41dd-97e4-75ff04004baa)

A presets:
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/3c24e5b9-f7fb-482a-bd63-639a95b153d2)

A methods:
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/9d8c209b-2f37-4ed3-8c34-c3424d95a991)

Loading two models in parallel locally:
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/7cd3b762-530b-4795-b8c3-3a269e916608)

Using them concurrently to make inferences:
![image](https://github.com/gabrielolympie/VisualAIFlows/assets/46057918/c3390fc2-d97b-409c-bdbf-8b2fb8d03d85)

# Next steps:
- Improving current experimental feature
- Design a flow framework that is homogenous with the current mecanisms
- Add credits for other projects (thanks Ironclad, Ollama, Huggingface, Mistral, Meta)
- Implement new routes for image generation, multimodel inputs etc.
- Make a proper documentation

# Hope you have fun with this toy project, enjoy!


