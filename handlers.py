# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy 

from collections.abc import Iterable

from .__init__ import get_addon_prefs
from .operators.palette import msgbus_palette_callback
from .customnodes import classes as allcustomnodes
from .customnodes import NODEBOOSTER_NG_GN_IsRenderedView


def _customnodes(nodes:list):
    """automatically run the update_all_instances() function of all custom nodes passed"""

    if (not nodes):
        return None

    sett_win = bpy.context.window_manager.nodebooster
    has_autorization = sett_win.authorize_automatic_execution

    for cls in nodes:

        if (not hasattr(cls,'update_all_instances')):
            print(f"WARNING: update_all_instances() function is required in your customnode class for an automatic execution.")
            continue

        #automatic re-evaluation of the Python Expression and Python Nex Nodes.
        #for security reasons, we update only if the user allows it expressively on each blender sess.
        if ('AUTORIZATION_REQUIRED' in cls.auto_update) and (not has_autorization):
            continue

        cls.update_all_instances(from_autoexec=True)
        continue

    return None


# We start with msgbusses


MSGBUSOWNER_VIEWPORT_SHADING = object()
MSGBUSOWNER_PALETTE =  object()

def msgbus_viewportshading_callback(*args):

    if (get_addon_prefs().debug_depsgraph):
        print("msgbus_viewportshading_callback(): msgbus signal")

    NODEBOOSTER_NG_GN_IsRenderedView.update_all_instances(from_autoexec=True)

    return None 

def register_msgbusses():
    
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.View3DShading, "type"),
        owner=MSGBUSOWNER_VIEWPORT_SHADING,
        notify=msgbus_viewportshading_callback,
        args=(None,),
        options={"PERSISTENT"},
        )
    bpy.msgbus.subscribe_rna(
        key=bpy.types.PaletteColor,
        owner=MSGBUSOWNER_PALETTE,
        notify=msgbus_palette_callback,
        args=(None,),
        options={"PERSISTENT"},
        )

    return None

def unregister_msgbusses():

    bpy.msgbus.clear_by_owner(MSGBUSOWNER_VIEWPORT_SHADING)
    bpy.msgbus.clear_by_owner(MSGBUSOWNER_PALETTE)

    return None


# Define the handlers functions


DEPSPOST_UPD_NODES = [cls for cls in allcustomnodes if ('DEPS_POST' in cls.auto_update)]

@bpy.app.handlers.persistent
def nodebooster_handler_depspost(scene,desp):
    """update on depsgraph change"""

    if (get_addon_prefs().debug_depsgraph):
        print("nodebooster_handler_depspost(): depsgraph signal")

    #updates for our custom nodes
    _customnodes(DEPSPOST_UPD_NODES)
    return None

FRAMEPRE_UPD_NODES = [cls for cls in allcustomnodes if ('FRAME_PRE' in cls.auto_update)]

@bpy.app.handlers.persistent
def nodebooster_handler_framepre(scene,desp):
    """update on frame change"""

    if (get_addon_prefs().debug_depsgraph):
        print("nodebooster_handler_framepre(): frame_pre signal")

    #updates for our custom nodes
    _customnodes(FRAMEPRE_UPD_NODES)
    return None

LOADPOST_UPD_NODES = [cls for cls in allcustomnodes if ('LOAD_POST' in cls.auto_update)]

@bpy.app.handlers.persistent
def nodebooster_handler_loadpost(scene,desp):
    """Handler function when user is loading a file"""
    
    if (get_addon_prefs().debug_depsgraph):
        print("nodebooster_handler_framepre(): frame_pre signal")

    #need to add message bus on each blender load
    register_msgbusses()

    #updates for our custom nodes
    _customnodes(LOADPOST_UPD_NODES)
    return None


# Registering the handlers


def all_handlers(name=False):
    """return a list of handler stored in .blend""" 

    for oh in bpy.app.handlers:
        if isinstance(oh, Iterable):
            for h in oh:
                yield h

def load_handlers():
    
    handler_names = [h.__name__ for h in all_handlers()]

    if ('nodebooster_handler_depspost' not in handler_names):
        bpy.app.handlers.depsgraph_update_post.append(nodebooster_handler_depspost)

    if ('nodebooster_handler_framepre' not in handler_names):
        bpy.app.handlers.frame_change_pre.append(nodebooster_handler_framepre)

    if ('nodebooster_handler_loadpost' not in handler_names):
        bpy.app.handlers.load_post.append(nodebooster_handler_loadpost)
        
    return None 

def unload_handlers():

    for h in all_handlers():

        if(h.__name__=='nodebooster_handler_depspost'):
            bpy.app.handlers.depsgraph_update_post.remove(h)

        if(h.__name__=='nodebooster_handler_framepre'):
            bpy.app.handlers.frame_change_pre.remove(h)

        if(h.__name__=='nodebooster_handler_loadpost'):
            bpy.app.handlers.load_post.remove(h)

    return None
