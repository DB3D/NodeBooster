# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy 

from ..__init__ import get_addon_prefs
from ..utils.str_utils import word_wrap
from ..utils.node_utils import (
    create_new_nodegroup,
    set_socket_defvalue,
    get_all_nodes,
)


def evaluate_sequencer_volume(frame=None,):
    """evaluate the sequencer volume source
    this node was possible thanks to tintwotin https://github.com/snuq/VSEQF/blob/3ac717e1fa8c7371ec40503428bc2d0d004f0b35/vseqf.py#L142"""

    #TODO ideally we need to also sample volume from few frame before or after, so user can create a smoothing falloff of some sort, 
    #     that's what 'frame_delay' is for, but unfortunately this function is incomplete, frame can only be None in order to work
    #     right now i do not have the strength to do it, you'll need to check for 'fades.get_fade_curve(bpy.context, sequence, create=False)' from the github link above

    scene = bpy.context.scene
    if (scene.sequence_editor is None):
        return 0

    totvolume = 0
    sequences = scene.sequence_editor.sequences_all
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    if (frame is None):
          frame = scene.frame_current
          evaluate_volume = False
    else: evaluate_volume = True

    fps = scene.render.fps / scene.render.fps_base

    for sequence in sequences:

        if ((sequence.type=='SOUND') and (sequence.frame_final_start<frame) 
            and (sequence.frame_final_end>frame) and (not sequence.mute)):
            
            time_from = (frame - 1 - sequence.frame_start) / fps
            time_to = (frame - sequence.frame_start) / fps

            audio = sequence.sound.evaluated_get(depsgraph).factory
            chunk = audio.limit(time_from, time_to).data()
            
            #sometimes the chunks cannot be read properly, try to read 2 frames instead
            if (len(chunk)==0):
                time_from_temp = (frame - 2 - sequence.frame_start) / fps
                chunk = audio.limit(time_from_temp, time_to).data()
                
            #chunk still couldnt be read...
            if (len(chunk)==0):
                average = 0

            else:
                cmax, cmin = abs(chunk.max()), abs(chunk.min())
                average = cmax if (cmax > cmin) else cmin

            if evaluate_volume:
                # TODO: for later? get fade curve https://github.com/snuq/VSEQF/blob/8487c256db536eb2e9288a16248fe394d06dfb74/fades.py#L57
                # fcurve = get_fade_curve(bpy.context, sequence, create=False)
                # if (fcurve):
                #       volume = fcurve.evaluate(frame)
                # else: volume = sequence.volume
                volume = 0
            else:
                volume = sequence.volume

            totvolume += (average * volume)
        
        continue 

    return float(totvolume)

# ooooo      ooo                 .o8            
# `888b.     `8'                "888            
#  8 `88b.    8   .ooooo.   .oooo888   .ooooo.  
#  8   `88b.  8  d88' `88b d88' `888  d88' `88b 
#  8     `88b.8  888   888 888   888  888ooo888 
#  8       `888  888   888 888   888  888    .o 
# o8o        `8  `Y8bod8P' `Y8bod88P" `Y8bod8P' 

class Base():
    
    bl_idname = "NodeBoosterSequencerVolume"
    bl_label = "Sequencer Volume"
    bl_description = """Custom Nodgroup: Evaluate the active sound level of the VideoSequencer editor.
    • Expect the value to be automatically updated on each on depsgraph post signals"""
    auto_update = {'FRAME_PRE','DEPS_POST',}
    tree_type = "*ChildrenDefined*"

    # frame_delay : bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        """mandatory poll"""
        return True

    def init(self,context,):        
        """this fct run when appending the node for the first time"""

        name = f".{self.bl_idname}"

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                tree_type=self.tree_type,
                out_sockets={
                    "Volume" : "NodeSocketFloat",
                    },
                )

        ng = ng.copy() #always using a copy of the original ng

        self.node_tree = ng
        self.width = 150
        self.label = self.bl_label

        return None 

    def copy(self,node,):
        """fct run when dupplicating the node"""
        
        self.node_tree = node.node_tree.copy()
        
        return None 
    
    def update(self):
        """generic update function"""
        
        ng = self.node_tree
        
        # for later?
        # frame = None 
        # if (self.frame_delay):
        #     frame = bpy.context.scene.frame_current + self.frame_delay

        set_socket_defvalue(ng,0,value=evaluate_sequencer_volume(),)

        return None
    
    def draw_label(self,):
        """node label"""
        
        return self.bl_label

    def draw_buttons(self,context,layout,):
        """node interface drawing"""
        
        #for later?
        #layout.prop(self,"frame_delay",text="Frame Delay")

        return None 

    def draw_panel(self, layout, context):
        """draw in the nodebooster N panel 'Active Node'"""
    
        n = self

        header, panel = layout.panel("doc_panelid", default_closed=True,)
        header.label(text="Documentation",)
        if (panel):
            word_wrap(layout=panel, alert=False, active=True, max_char='auto',
                char_auto_sidepadding=0.9, context=context, string=n.bl_description,
                )
            panel.operator("wm.url_open", text="Documentation",).url = "https://blenderartists.org/t/nodebooster-new-nodes-and-functionalities-for-node-wizards-for-free"
            
        header, panel = layout.panel("dev_panelid", default_closed=True,)
        header.label(text="Development",)
        if (panel):
            panel.active = False
                            
            col = panel.column(align=True)
            col.label(text="NodeTree:")
            col.template_ID(n, "node_tree")

        return None

    @classmethod
    def update_all_instances(cls, from_autoexec=False,):
        """search for all nodes of this type and update them"""

        #TODO we call update_all_instances for a lot of nodes from depsgraph & we need to optimize this, because func below may recur a LOT of nodes
        # could pass a from_nodes arg in this function
        for n in get_all_nodes(
            geometry=True, compositing=True, shader=True, 
            ignore_ng_name="NodeBooster", match_idnames={cls.bl_idname},
            ): 
            n.update()

        return None

#Per Node-Editor Children:
#Respect _NG_ + _GN_/_SH_/_CP_ nomenclature

class NODEBOOSTER_NG_GN_SequencerVolume(Base, bpy.types.GeometryNodeCustomGroup):
    tree_type = "GeometryNodeTree"
    bl_idname = "GeometryNode" + Base.bl_idname

class NODEBOOSTER_NG_SH_SequencerVolume(Base, bpy.types.ShaderNodeCustomGroup):
    tree_type = "ShaderNodeTree"
    bl_idname = "ShaderNode" + Base.bl_idname

class NODEBOOSTER_NG_CP_SequencerVolume(Base, bpy.types.CompositorNodeCustomGroup):
    tree_type = "CompositorNodeTree"
    bl_idname = "CompositorNode" + Base.bl_idname