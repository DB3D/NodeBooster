# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later

#TODO bake operator in panel as well, like math
#TODO auto generated Nex gloassary in text editor

import bpy

import re, traceback

from ..__init__ import get_addon_prefs
from ..resources import cust_icon
from ..nex.nextypes import NexFactory, NexError
from ..utils.str_utils import word_wrap
from ..utils.node_utils import (
    get_socket,
    create_socket,
    create_new_nodegroup,
    set_socket_defvalue,
    remove_socket,
    set_socket_label,
    get_socket_type,
    set_socket_type,
    get_farest_node,
)


def transform_nex_script(original_text:str, nextypes:list) -> str:
    """
    Transforms a Nex script:
    - Remove comments
    - Replace with custom Nex type declarations 
        "VAR : TYPE = RESTOFTHELINE" → "VAR = TYPE('VAR', RESTOFTHELINE)"
        "VAR : TYPE"                 → "VAR = TYPE('VAR', None)"
    """

    #TODO support ';' python notation?

    def replacer(match):
        varname = match.group(1)
        typename = match.group(2)
        rest = match.group(3)
        if (rest is None or rest.strip() == ''):
              return f"{varname} = {typename}('{varname}', None)"
        else: return f"{varname} = {typename}('{varname}', {rest.strip()})"

    pattern = re.compile(rf"\b(\w+)\s*:\s*({'|'.join(nextypes)})\s*(?:=\s*(.+))?")
    
    lines = []
    for line in original_text.splitlines():

        # Remove comments: delete anything from a '#' to the end of the line.
        line = re.sub(r'#.*', '', line)

        # ignore white lines
        if (len(line)==0):
            continue

        #transform type hinting notation
        line = pattern.sub(replacer, line)

        lines.append(line)
        continue

    return '\n'.join(lines)

# unused for now
# def extract_nex_variables(script:str, nextypes:list) -> str:
#     """Extracts variable names and their Nex types from the given script."""
    
#     # Create a regex pattern to match lines like "varname : nexType = ..."
#     pattern = re.compile(
#         r"^\s*(\w+)\s*:\s*(" + "|".join(nextypes) + r")\s*=",
#         re.MULTILINE
#     )
#     return pattern.findall(script)


class NODEBOOSTER_NG_nexinterpreter(bpy.types.GeometryNodeCustomGroup):
    """Custom NodeGroup: Executes a Python script containing 'Nex' language. 'Nex' stands for nodal expression.\
    With Nex, you can efficiently and easily interpret python code into Geometry-Node nodal programming.
    • WIP text about synthax.
    • WIP text about how it works"""

    #TODO Optimization: node_utils function should check if value or type isn't already set before setting it.
    #TODO maybe should add a nodebooster panel in text editor for quick execution?

    bl_idname = "GeometryNodeNodeBoosterNexInterpreter"
    bl_label = "Python Nex Script (WIP)"
    # bl_icon = 'SCRIPT'

    error_message : bpy.props.StringProperty(
        description="User interface error message",
        )
    debug_evaluation_counter : bpy.props.IntProperty(
        name="Execution Counter",
        default=0,
        )
    debug_nodes_quantity : bpy.props.IntProperty(
        name="Number of nodes in the nodetree",
        default=-1,
        )
    user_textdata : bpy.props.PointerProperty(
        type=bpy.types.Text,
        name="TextData",
        description="Blender Text datablock to execute",
        poll=lambda self, data: not data.name.startswith('.'),
        update=lambda self, context: self.interpret_nex_script(rebuild=True) if (self.user_textdata is None) else None,
        )
    execute_script : bpy.props.BoolProperty(
        name="Execute",
        description="Click here to execute the Nex script & re-building the generated node-tree",
        update=lambda self, context: self.interpret_nex_script(rebuild=True),
        )
    execute_at_depsgraph : bpy.props.BoolProperty(
        name="Automatically Refresh",
        description="Synchronize the interpreted python constants (if any) with the outputs values on each depsgraph frame and interaction. By toggling this option, your Nex script will be executed constantly on each interaction you have with blender (note that the internal nodetree will not be constantly rebuilt, press the Play button to do so.).",
        default=False,
        )

    def init(self, context):
        """Called when the node is first added."""

        name = f".{self.bl_idname}"

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                out_sockets={
                    "Error" : "NodeSocketBool",
                },
            )

        ng = ng.copy() #always using a copy of the original ng

        self.node_tree = ng
        self.width = 185
        self.label = self.bl_label

        return None

    def copy(self,node,):
        """fct run when dupplicating the node"""

        self.node_tree = node.node_tree.copy()

        return None 

    def update(self):
        """generic update function"""

        return None

    def cleanse_sockets(self, in_protectednames=None, out_protectednames=None,):
        """remove all our sockets except error socket
        optional: except give list of names"""

        ng = self.node_tree
        in_nod, out_nod = ng.nodes["Group Input"], ng.nodes["Group Output"]

        for mode in ('INPUT','OUTPUT'):
            sockets = in_nod.outputs if (mode=='INPUT') else out_nod.inputs
            protected = in_protectednames if (mode=='INPUT') else out_protectednames

            idx_to_del = []
            for idx,socket in enumerate(sockets):

                #skip custom sockets
                if (socket.type=='CUSTOM'):
                    continue

                #skip error socket, is the first output..
                if (mode=='OUTPUT' and idx==0):
                    continue

                #deletion by name? if passed
                if (protected):
                    if (socket.name not in protected):
                        idx_to_del.append(idx)
                    continue

                idx_to_del.append(idx)

                #protection is only valid once, we do remove doubles
                if (protected):
                    protected.remove(socket.name)

                continue

            for idx in reversed(idx_to_del):
                remove_socket(ng, idx, in_out=mode,)

        return None

    def cleanse_nodes(self):
        """remove any added nodes in the nodetree"""

        ng = self.node_tree

        for node in list(ng.nodes).copy():
            if (node.name not in {"Group Input", "Group Output", "ScriptStorage",}):
                ng.nodes.remove(node)

        #move output near to input again..
        in_nod, out_nod = ng.nodes["Group Input"], ng.nodes["Group Output"]
        out_nod.location = in_nod.location
        out_nod.location.x += 200

        self.debug_nodes_quantity = -1
        return None

    def store_text_data_as_frame(self, text):
        """we store the user text data as a frame"""

        ng = self.node_tree

        frame = ng.nodes.get("ScriptStorage")
        if (frame is None):
            frame = ng.nodes.new('NodeFrame')
            frame.name = frame.label = "ScriptStorage"
            frame.width = 500
            frame.height = 1500
            frame.location.x = -750
            frame.label_size = 8

        if (frame.text!=text):
            frame.text = text

        return None

    def interpret_nex_script(self, rebuild=False):
        """Execute the Python script from a Blender Text datablock, capture local variables whose names start with "out_",
        and update the node group's output sockets accordingly."""

        ng = self.node_tree
        in_nod, out_nod = ng.nodes["Group Input"], ng.nodes["Group Output"]
        self.debug_evaluation_counter += 1 # potential issue with int limit here? idk how blender handle this
        self.error_message = ''

        #we reset the Error status back to false
        set_socket_label(ng,0, label="NoErrors",)
        set_socket_defvalue(ng,0, value=False,)
        self.error_message = ''

        #Keepsafe the text data as extra user
        self.store_text_data_as_frame(self.user_textdata)

        # Check if a Blender Text datablock has been specified
        if (self.user_textdata is None):
            #cleanse all sockets and nodes then
            self.cleanse_sockets()
            self.cleanse_nodes()
            # set error to True
            set_socket_label(ng,0, label="VoidTextError",)
            set_socket_defvalue(ng,0, value=True,)
            return None

        user_script = self.user_textdata.as_string()
        
        #capture the inputs/outputs later on execution.
        all_inputs_names = []
        all_outputs_names = []
        kwargs = all_inputs_names, all_outputs_names
        
        #define all possible Nex types & functions the user can toy with
        #TODO maybe it's best that the factory is executed only once. There's a lot of procedural typedef here..
        nexfunctions = NexFactory(self, 'NexFunctions',)
        nexintypes = {
            # NodeSocketBool
            # NodeSocketInt
            'infloat': NexFactory(self, 'NexFloat', '', *kwargs,),
            'invec': NexFactory(self, 'NexVec', '', *kwargs,),
            # NodeSocketColor
            # NodeSocketRotation
            # NodeSocketMatrix
            }
        nexoutypes = {
            'outbool': NexFactory(self, 'NexOutput', 'NodeSocketBool', *kwargs,),
            'outint': NexFactory(self, 'NexOutput', 'NodeSocketInt', *kwargs,),
            'outfloat': NexFactory(self, 'NexOutput', 'NodeSocketFloat', *kwargs,),
            'outvec': NexFactory(self, 'NexOutput', 'NodeSocketVector', *kwargs,),
            'outcol': NexFactory(self, 'NexOutput', 'NodeSocketColor', *kwargs,),
            'outquat': NexFactory(self, 'NexOutput', 'NodeSocketRotation', *kwargs,),
            'outmat': NexFactory(self, 'NexOutput', 'NodeSocketMatrix', *kwargs,),
            'outauto': NexFactory(self, 'NexOutput', '',                *kwargs,),
            }
        nextypes = {**nexintypes, **nexoutypes}

        # Synthax:
        # replace varname:infloat=REST with varname=infloat('varname',REST) & remove comments
        # much better workflow for artists to use python type indications IMO
        final_script = transform_nex_script(user_script, nextypes.keys(),)
        
        #did the user changes stuff in the script?
        cache_script = ''
        cache_name = f".boostercache.{self.user_textdata.name}"
        cache_text = bpy.data.texts.get(cache_name)
        if (cache_text is not None):
              cache_script = cache_text.as_string()
        is_dirty = (final_script!=cache_script)
        
        # If user modified the script, the script will need a rebuild.
        if (is_dirty or rebuild):

            #Clean up nodes.. we'll rebuild the nodetree
            self.cleanse_nodes()

            # We set the first node active (node arrangement in nodesetter.py module is based on active)
            ng.nodes.active = in_nod
            
            #when initalizing the NexTypes, the inputs/outputs sockets will be created.
        
        # Namespace, we inject Nex types in user namespace
        exec_namespace = {}
        exec_namespace.update(nextypes)
        exec_namespace.update(nexfunctions)
        script_vars = {} #catch variables from exec?

        # for debug mode, we execute without try except to catch 'real' errors with more details. 
        # the exception we raise are designed for the users, not for ourselves devs
        if (get_addon_prefs().debug):

            i = self.debug_evaluation_counter
            print(f"\n{'-'*50}")

            print(f"USER EXPRESSION: exec{i}")
            print('"""\n'+user_script+'\n"""')

            print(f"TRANSFORMED EXPRESSION: exec{i}")
            print('"""\n'+final_script+'\n"""')

            print(f"ERROR(?): exec{i}")
            exec(final_script, exec_namespace, script_vars)

        try:
            exec(final_script, exec_namespace, script_vars)

        except NexError as e:
            # set error to True
            set_socket_label(ng,0, label="NexError",)
            set_socket_defvalue(ng,0, value=True,)
            # Display error
            self.error_message = str(e)
            # Cleanse nodes, there was an error anyway, the current nodetree is tainted..
            self.cleanse_nodes()
            return None

        except Exception as e:
            print(f"\n{self.bl_idname} Python Execution Exception '{type(e).__name__}':\n{e}\n")
            #print more information
            print("Full Traceback Error:")
            traceback.print_exc()
            # set error to True
            set_socket_label(ng,0, label="PythonError",)
            set_socket_defvalue(ng,0, value=True,)
            # Display error
            self.error_message = f"{type(e).__name__}. {e}. See console for traceback."
            return None

        #check on vars..
        #make sure there are Nex types in the user expression
        if len(all_inputs_names + all_outputs_names)==0:
            #cleanse all sockets and nodes then
            self.cleanse_sockets()
            self.cleanse_nodes()
            # set error to True
            set_socket_label(ng,0, label="VoidNexError",)
            set_socket_defvalue(ng,0, value=True,)
            # Display error
            self.error_message = f"No Nex Found in Script. An example of Nex code can be found in 'Text Editor > Template > Booster Scripts'"
            return None
        #also make sure there are Nex outputs types in there..
        if len(all_outputs_names)==0:
            # set error to True
            set_socket_label(ng,0, label="NoOutputError",)
            set_socket_defvalue(ng,0, value=True,)
            # Display error
            self.error_message = f"Mandatory Outputs not Found. An example of Nex code can be found in 'Text Editor > Template > Booster Scripts'"
            return None
                
        # Clean up leftover sockets from previous run which created sockets no longer in use
        self.cleanse_sockets(
            in_protectednames=all_inputs_names,
            out_protectednames=all_outputs_names,
            )

        #we cache the script it correspond to current nodetree arrangements, keep track of modifications
        if (cache_text is None):
            cache_text = bpy.data.texts.new(cache_name)
        if (is_dirty):
            cache_text.clear()
            cache_text.write(final_script)

        #we count the number of nodes
        self.debug_nodes_quantity = len(ng.nodes)

        #Clean up the nodetree spacing a little, for the output node
        if (is_dirty or rebuild):
            farest = get_farest_node(ng)
            if (farest!=out_nod):
                out_nod.location.x = farest.location.x + 250

        return None
    
    def free(self):
        """when user delete the node we need to clean up"""
        
        self.user_textdata = None

        return None

    def draw_label(self,):
        """node label"""

        return self.bl_label

    def draw_buttons(self, context, layout,):
        """node interface drawing"""

        sett_win = context.window_manager.nodebooster
        is_error = bool(self.error_message)
        animated_icon = f"W_TIME_{self.debug_evaluation_counter%8}"

        layout.separator(factor=0.25)

        col = layout.column(align=True)
        row = col.row(align=True)

        field = row.row(align=True)
        field.alert = is_error
        field.prop(self, "user_textdata", text="", icon="TEXT", placeholder="NexScript.py",)

        prop = row.row(align=True)
        prop.enabled = sett_win.allow_auto_exec
        prop.prop(self, "execute_at_depsgraph", text="", icon_value=cust_icon(animated_icon),)

        row.prop(self, "execute_script", text="", icon="PLAY", invert_checkbox=self.execute_script,)

        if (not sett_win.allow_auto_exec):
            col.separator(factor=0.75)
            col.prop(sett_win,"allow_auto_exec")

        if (is_error):
            col = col.column(align=True)
            col.separator(factor=2)
            word_wrap(layout=col, alert=True, active=True, max_char=self.width/5.75, string=self.error_message,)

        layout.separator(factor=0.5)

        return None

    @classmethod
    def update_all_instances(cls, from_depsgraph=False,):
        """search for all nodes of this type and update them"""


        all_instances = [n for ng in bpy.data.node_groups for n in ng.nodes if (n.bl_idname==cls.bl_idname)]
        for n in all_instances:
            if (from_depsgraph and not n.execute_at_depsgraph):
                continue
            if (n.mute):
                continue
            n.interpret_nex_script()
            continue

        return None

