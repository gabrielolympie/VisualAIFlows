import yaml
import numpy as np
import pandas as pd

choice="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789-_"

def make_id():
    return "".join(np.random.choice(list(choice), size=21))

def indent(s, n=1):
    for _ in range(n):
        s = s.replace("\n","\n    ")
    return s

graph_input_template="""'[{node_id}]:graphInput "{name}"':
    data:
        dataType: {datatype}
        defaultValue: {value}
        editor: {datatype}
        id: {name}
        useDefaultValueInput: false
    outgoingConnections:{connections}
    visualData: -500/{y}/400/800//"""

graph_output_template="""'[{node_id}]:graphOutput "Graph Output"':
    data:
        dataType: {datatype}
        id: {id}
    visualData: 1000/{y}/400/800//"""

destructure_template="""'[{node_id}]:destructure "Destructure"':
    data:
        paths:{template}    
    outgoingConnections:{connections}    
    visualData: 500/0/400/800//"""

object_template="""'[{node_id}]:object "Object"':
    data:
        jsonTemplate: |-{template}
    
    outgoingConnections:{connections}
    
    visualData: 0/{y}/400/800//"""

graph_template="""
    metadata:
        description: {graph_description}
        id: {graph_id}
        name: {graph_name}
    nodes:"""

playground_template="""
metadata:
    description: {name}
    id: {graph_id}
    name: {name}
nodes:"""

comment_template="""'[{node_id}]:comment "Playground"':
    data:
        backgroundColor: {background_color}
        color: rgba(255,255,255,1)
        height: {h}
        text: "{text}"
    visualData: {x}/{y}/{w}/{h}//"""

sub_graph_template="""'[{node_id}]:subGraph "{graph_name}"':
    data:
        graphId: {graph_id}
        useAsGraphPartialOutput: false
        useErrorOutput: false
        height: 400
    outgoingConnections:
    visualData: {x}/{y}/500/400//"""

prompt_template="""'[{node_id}]:text "{graph_name}"':
    data:
        text: "{text}"
    visualData: {x}/{y}/500/400//"""

http_template="""'[{node_id}]:httpCall "HTTP CALL"':
    data:
        body: ""
        errorOnNon200: true
        headers: ""
        jsonTemplate: ""
        method: POST
        text: ""
        url: {api_endpoint}
        useBodyInput: true
        useHeadersInput: true
        useMethodInput: false
        useUrlInput: false
    outgoingConnections:{connections}
    visualData: 500/0/400/800//"""

def make_prompt_template(
    graph_name="",
    text="",
    v_padding=0,
    h_padding=0,
):
    node_id=make_id()
    return node_id, prompt_template.format(
        node_id=node_id,
        graph_name=graph_name,
        text=text,
        x=h_padding,
        y=v_padding,
    )

def make_graph_input(name:str, datatype:str, value, connections:str, vertical_position:float=0):
    node_id=make_id()
    return node_id, graph_input_template.format(node_id=node_id,name=name,datatype=datatype,value=value, connections=connections, y=vertical_position)

def make_graph_output(datatype:str, id:str, vertical_position:float=0):
    node_id=make_id()
    return node_id, graph_output_template.format(node_id=node_id, datatype=datatype, id=id, y=vertical_position)

def make_destructure(template:str, connections:str):
    node_id=make_id()
    return node_id, destructure_template.format(node_id=node_id, template=template, connections=connections)

def make_http_call(api_endpoint:str, connections:str):
    node_id=make_id()
    template=http_template.format(node_id=node_id, api_endpoint=api_endpoint, connections=connections)#, headers=headers)
    return node_id, template

def make_sub_graph(graph_name:str, graph_id, horizontal_position:float=0, vertical_position:float=0):
    node_id=make_id()
    return node_id, sub_graph_template.format(node_id=node_id, graph_id=graph_id, graph_name=graph_name, x=horizontal_position, y=vertical_position)

def make_comment(
    background_color='rgba(33,61,195,0.36)',
    text="## Playground",
    v_padding=0,
    h_padding=0,
    height=0,
    width=0
):
    node_id=make_id()
    return node_id, comment_template.format(
        node_id=node_id,
        text=text,
        background_color=background_color,
        x=h_padding,
        y=v_padding,
        h=height,
        w=width
    )
    
def dict_to_object(dico, datatype):
    output=[]
    for k,v in dico.items():
        if datatype=="number":
            output.append(f'\n"{k}":{v}')
        else:
            output.append(f'\n"{k}":"{v}"')
        
    output= '\n{'+indent(','.join(output))+'\n}'
    return output

def make_object(template:str, connections:str,vertical_position:float=0):
    node_id=make_id()
    return node_id, object_template.format(node_id=node_id, template=template, connections=connections,y=vertical_position)

def make_presets_graph(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    graph_id=config['graph_id']
    graph=graph_template.format(
        graph_id=config['graph_id'],
        graph_name=config['graph_name'],
        graph_description=config['graph_description']
    )
    
    nodes=[]
    ## Add output First
    
    parent_template=[""]
    parent_connections=[""]
    
    for i, (k, v) in enumerate(config['values'].items()):
        node_id, node = make_graph_output(
            datatype=config['values_type'],
            id=k,
            vertical_position= i * 150
        )
        nodes.append(node)
        parent_template.append(f"  - {k}")
        parent_connections.append(f'  - match_{i}->"Graph Output" {node_id}/value')
    parent_template=indent("\n".join(parent_template), 3)
    parent_connections=indent("\n".join(parent_connections),3)

    ## Add destructure
    node_id, node=make_destructure(parent_template, parent_connections)
    nodes.append(node)

    ## Add Origin
    parent_template=dict_to_object(config['values'], config['values_type'])
    parent_connections=f'\n  - output->"Destructure" {node_id}/object'
    node_id, node=make_object(indent(parent_template,3), indent(parent_connections, 3))
    nodes.append(node)
    nodes.reverse()
    graph+=indent('\n'+'\n'.join(nodes), 2)
    return graph_id, graph

def make_method_graph(path, api_base):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    graph_id=config['graph_id']
    graph=graph_template.format(
        graph_id=config['graph_id'],
        graph_name=config['graph_name'],
        graph_description=config['graph_description']
    )
    
    nodes=[]
    ## Add output First
    
    parent_template=[""]
    parent_connections=[""]
    
    for i, (k, v) in enumerate(config['outputs'].items()):
        node_id, node = make_graph_output(
            datatype=v,
            id=k,
            vertical_position= i * 150
        )
        nodes.append(node)
        parent_template.append(f"  - {k}")
        parent_connections.append(f'  - res_body->"Graph Output" {node_id}/value')
    parent_template=indent("\n".join(parent_template), 3)
    parent_connections=indent("\n".join(parent_connections),3)

    ## Add http call
    node_id, node=make_http_call(f"{api_base}{config['fast_api_route']}", parent_connections)
    nodes.append(node)

    ## Add Header
    dico={"Content-Type": "application/json"}
    parent_template=dict_to_object(dico, 'string')
    parent_connections=f'\n  - output->"HTTP CALL" {node_id}/headers'
    
    temp_node_id, node=make_object(indent(parent_template,3), indent(parent_connections, 3), vertical_position=-200)
    nodes.append(node)
    
    ## Add object
    dico={elt: " {{ "+elt+" }}" for elt in config['inputs']}
    parent_template=dict_to_object(dico, 'number')
    parent_connections=f'\n  - output->"HTTP CALL" {node_id}/req_body'
    
    node_id, node=make_object(indent(parent_template,3), indent(parent_connections, 3))
    nodes.append(node)
    
    # ## Add Inputs
    for i, (k, v) in enumerate(config['inputs'].items()):
        parent_connections=indent(f"""\n  - 'data->"Object" {node_id}/ {k} '""")
        input_node_id, node = make_graph_input(
            name=k,
            datatype=v['data_type'],
            value=v['value'],
            connections=parent_connections,
            vertical_position= i * 150
        )
        nodes.append(node)
        
    nodes.reverse()
    graph+=indent('\n'+'\n'.join(nodes), 2)
    return graph_id, graph

def get_comments(height=4000, width=16000, padding=200, secondary_padding=50):
    comments={}
    comments['methods']={
        'background_color':'rgba(254,152,154,0.3)',
        'text':"## Methods",
        'v_padding':padding,
        'h_padding':padding,
        'height':600,
        'width':width - 2*padding,
    }
    comments['prompts']={
        'background_color':'rgba(230,254,115,0.3)',
        'text':"## Prompts",
        'h_padding':padding,
        'v_padding':height - padding - 1200,
        'height':1200,
        'width':width - 2*padding,
    }
    comments['presets']={
        'background_color':'rgba(120,245,206,0.3)',
        'text':"## Presets",
        'v_padding':padding + 600 + secondary_padding,
        'h_padding':padding,
        'height':height - 2*padding - 3*600 - 2 * secondary_padding,
        'width':600,
    }
    comments['flows']={
        'background_color':'rgba(62,52,255,0.3)',
        'text':"## Flows",
        'h_padding':padding + 600 + secondary_padding,
        'v_padding':padding + 600 + secondary_padding,
        'height':height - 2*padding - 3*600 - 2 * secondary_padding,
        'width':width - 2*padding - 600 - secondary_padding,
    }
    return comments

def make_playground_graph(graph_name, graph_ids,prompts={}, height=4000, width=16000, padding=200, secondary_padding=50):
    graph_id=make_id()
    graph=playground_template.format(name=graph_name, graph_id=graph_id)
    

    ## Adding comments
    comments=[make_comment(**item)[1] for key, item in get_comments(height=height, width=width, padding=padding, secondary_padding=secondary_padding).items()]
    graph+= indent('\n'+'\n'.join(comments), 1)
    
    nodes=[]
    ## Adding Prompt Templates
    g,p=0,0
    for group in prompts:
        for prompt in prompts[group]:
            prompt_name=prompt
            
            prompt_content='\\n'.join(prompts[group][prompt_name])
            node_id, node=make_prompt_template(
                graph_name=prompt_name,
                text=prompt_content,
                v_padding=height - padding - 1200 + 200 + 200*p,
                h_padding=padding + padding + 600*g + 50,
            )
            nodes.append(node)
            p+=1
        p=0
        g+=1

    p,m,f=0,0,0
    for k,v in graph_ids.items():
        if k.split('/')[0]=='presets':
            node_id, node=make_sub_graph(graph_name=k.split('/')[1],graph_id=v, horizontal_position=padding + 50, vertical_position=1000+250*p)
            p+=1
            
        if k.split('/')[0]=='methods':
            node_id, node=make_sub_graph(graph_name=k.split('/')[1],graph_id=v, horizontal_position=600*m + padding + 50, vertical_position=padding + 200)
            m+=1
    
        if k.split('/')[0]=='flows':
            node_id, node=make_sub_graph(graph_name=k.split('/')[1],graph_id=v, horizontal_position=1000+600*f, vertical_position=1000)
            f+=1
        nodes.append(node)
    graph+= indent('\n'+'\n'.join(nodes), 1)
    return graph_id, graph
    
root ="""version: 4
data:"""

def export_preset(preset):
    graph_id, graph=make_presets_graph(f'models/presets/{preset}.yaml')
    standalone=root+graph
    with open(f'components/presets/{preset}.rivet-graph', 'w') as f:
        f.write(standalone)
    return graph_id, graph

def export_method(method, api_base="http://localhost:8000"):
    graph_id, graph=make_method_graph(f'models/methods/{method}.yaml', api_base=api_base)
    standalone=root+graph
    with open(f'components/methods/{method}.rivet-graph', 'w') as f:
        f.write(standalone)
    return graph_id, graph

def export_flow(flow, api_base="http://localhost:8000"):
    pass

def export_playground(graph_name, graph_ids,prompts={},  height=4000, width=16000, padding=200, secondary_padding=50):
    graph_id, graph=make_playground_graph(graph_name=graph_name, graph_ids=graph_ids,prompts=prompts, height=height, width=width, padding=padding, secondary_padding=secondary_padding)
    standalone=root+indent(graph)
    with open(f'./components/{graph_name}.rivet-graph', 'w') as f:
        f.write(standalone)
    return graph_id, graph


def read_and_process_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()

        # Create DataFrame from the file data
        df = pd.DataFrame({'text': data.split('\n')})

        # Assign group numbers based on occurrence of 'metadata:'
        df['group']=df['text'].apply(lambda x:'metadata:' in x)*1
        df['group']=df['group'].cumsum()
        df['group']=list(df['group'].values[1:]) + [df['group'].max()]
        df['group'].fillna(df['group'].max(), inplace=True)
        legacy_graphs=[]
        for group_num, group_df in df.groupby('group'):
            text = "\n".join(group_df['text'])
            if not('name: Playground\n' in text) and not('name: presets/' in text) and not('name: methods/' in text) and not('name: flows/' in text) and group_num >= 2:
                if "nodes:" in text:
                    legacy_graphs.append(text)
        return legacy_graphs
    except:
        print('Project does not exist, creating a new one')
        return None


project_template="""
version: 4
data:
    attachedData:
        trivet:
            testSuites: []
            version: 1
    metadata:
        description: ""
        id: QkvHJSzDtqoRAkiGj-t19
        mainGraphId: {playground_id}
        title: {name}
    plugins: []
    graphs:"""

def build_project(
    name,
    presets=[],
    methods=[],
    flows=[],
    prompts={},
    api_base="http://localhost:8000",
    height=4000,
    width=16000,
    padding=200,
    secondary_padding=50,
):

    legacy_graphs=read_and_process_file(f'{name}.rivet-project')
    graphs=[]
    graph_ids={}    
    for preset in presets:
        print(preset)
        graph_id, graph=export_preset(preset)
        graph_ids[f'presets/{preset}']=graph_id
        graphs.append('\n'+graph_id+":"+graph)

    for method in methods:
        print(method)
        graph_id, graph=export_method(method,api_base=api_base)
        graph_ids[f'methods/{method}']=graph_id
        graphs.append('\n'+graph_id+":"+graph)

    for flow in flows:
        print(flow)
        graph_id, graph=export_method(flow, api_base=api_base)
        graph_ids[f'flows/{flow}']=graph_id
        graphs.append('\n'+graph_id+":"+graph)

    playground_id, playground=export_playground("Playground", graph_ids, prompts=prompts,  height=height, width=width, padding=padding, secondary_padding=secondary_padding)
    graphs.append('\n'+playground_id+":"+indent(playground))
    
    graph=project_template.format(name=name, playground_id=playground_id) + indent("".join(graphs),2)
    if legacy_graphs:
        graph+=indent('\n'+"\n".join(legacy_graphs))

    with open(f'{name}.rivet-project', 'w') as f:
        f.write(graph)
    
    return graph_ids, graph