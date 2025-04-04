# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


from .sockets.custom_sockets import (
        NODEBOOSTER_SK_Interpolation,
        NODEBOOSTER_ND_CustomSocketUtility,
        )
from . camerainfo import (
        NODEBOOSTER_NG_GN_CameraInfo,
        NODEBOOSTER_NG_SH_CameraInfo,
        NODEBOOSTER_NG_CP_CameraInfo,
        )
from . lightinfo import (
        NODEBOOSTER_NG_GN_LightInfo,
        NODEBOOSTER_NG_SH_LightInfo,
        NODEBOOSTER_NG_CP_LightInfo,
        )
from . sceneinfo import (
        NODEBOOSTER_NG_GN_SceneInfo,
        NODEBOOSTER_NG_SH_SceneInfo,
        NODEBOOSTER_NG_CP_SceneInfo,
        )
from . renderinfo import (
        NODEBOOSTER_NG_GN_RenderInfo,
        NODEBOOSTER_NG_SH_RenderInfo,
        NODEBOOSTER_NG_CP_RenderInfo,
        )
from .rnainfo import (
        NODEBOOSTER_NG_GN_RNAInfo,
        NODEBOOSTER_NG_SH_RNAInfo,
        NODEBOOSTER_NG_CP_RNAInfo,
        )
from . isrenderedview import (
        NODEBOOSTER_NG_GN_IsRenderedView,
        )
from . sequencervolume import (
        NODEBOOSTER_NG_GN_SequencerSound,
        NODEBOOSTER_NG_SH_SequencerSound,
        NODEBOOSTER_NG_CP_SequencerSound,
        )
from . mathexpression import (
        NODEBOOSTER_NG_GN_MathExpression,
        NODEBOOSTER_NG_SH_MathExpression,
        NODEBOOSTER_NG_CP_MathExpression,
        )
from . pyexpression import (
        NODEBOOSTER_NG_GN_PyExpression,
        NODEBOOSTER_NG_SH_PyExpression,
        NODEBOOSTER_NG_CP_PyExpression,
        )
from . pynexscript import (
        NODEBOOSTER_NG_GN_PyNexScript,
        NODEBOOSTER_NG_SH_PyNexScript,
        NODEBOOSTER_NG_CP_PyNexScript,
        )
from . deviceinput import (
        NODEBOOSTER_NG_GN_DeviceInput,
        NODEBOOSTER_NG_SH_DeviceInput,
        NODEBOOSTER_NG_CP_DeviceInput,
        )
from . objectvelocity import (
        NODEBOOSTER_NG_GN_ObjectVelocity,
        NODEBOOSTER_NG_SH_ObjectVelocity,
        NODEBOOSTER_NG_CP_ObjectVelocity,
        )
from . interpolation.interpolationinput import (
        NODEBOOSTER_NG_GN_InterpolationInput,
        NODEBOOSTER_NG_SH_InterpolationInput,
        NODEBOOSTER_NG_CP_InterpolationInput,
        )
from . interpolation.interpolationinput import NODEBOOSTER_OT_interpolation_input_update
from . interpolation.interpolationmap import (
        NODEBOOSTER_NG_GN_InterpolationMap,
        NODEBOOSTER_NG_SH_InterpolationMap,
        NODEBOOSTER_NG_CP_InterpolationMap,
        )

# For menus, in order of appearance
# NOTE Redudancy. Perhaps menus.py could be refactored to use the _GN_, _SH_, _CP_ notations.

GN_CustomNodes = (
    ('Inputs',(
        NODEBOOSTER_NG_GN_RNAInfo,
        NODEBOOSTER_NG_GN_LightInfo,
        NODEBOOSTER_NG_GN_SceneInfo,
        NODEBOOSTER_NG_GN_RenderInfo,
        NODEBOOSTER_NG_GN_CameraInfo,
        NODEBOOSTER_NG_GN_ObjectVelocity,
        NODEBOOSTER_NG_GN_DeviceInput,
        NODEBOOSTER_NG_GN_IsRenderedView, #this one doesn't make sense in other editors.
        NODEBOOSTER_NG_GN_SequencerSound, ),
    ),
    ('Experimental',(
        NODEBOOSTER_NG_GN_InterpolationInput,
        NODEBOOSTER_NG_GN_InterpolationMap,
        NODEBOOSTER_ND_CustomSocketUtility, ), #dev utility.
    ), 
    (NODEBOOSTER_NG_GN_MathExpression),
    (NODEBOOSTER_NG_GN_PyExpression),
    (NODEBOOSTER_NG_GN_PyNexScript),
    )

SH_CustomNodes = (
    ('Inputs',(
        NODEBOOSTER_NG_SH_RNAInfo,
        NODEBOOSTER_NG_SH_LightInfo,
        NODEBOOSTER_NG_SH_SceneInfo,
        NODEBOOSTER_NG_SH_RenderInfo,
        NODEBOOSTER_NG_SH_CameraInfo,
        NODEBOOSTER_NG_SH_ObjectVelocity,
        NODEBOOSTER_NG_SH_DeviceInput,
        NODEBOOSTER_NG_SH_SequencerSound, ),
    ),
    ('Experimental',(
        NODEBOOSTER_NG_SH_InterpolationInput,
        NODEBOOSTER_NG_SH_InterpolationMap,
        NODEBOOSTER_ND_CustomSocketUtility, ), #dev utility.    
    ), 
    (NODEBOOSTER_NG_SH_MathExpression),
    (NODEBOOSTER_NG_SH_PyExpression),
    (NODEBOOSTER_NG_SH_PyNexScript),
    )

CP_CustomNodes = (
    ('Inputs',(
        NODEBOOSTER_NG_CP_RNAInfo,
        NODEBOOSTER_NG_CP_LightInfo,
        NODEBOOSTER_NG_CP_SceneInfo,
        NODEBOOSTER_NG_CP_RenderInfo,
        NODEBOOSTER_NG_CP_CameraInfo,
        NODEBOOSTER_NG_CP_ObjectVelocity,
        NODEBOOSTER_NG_CP_DeviceInput,
        NODEBOOSTER_NG_CP_SequencerSound, ),
    ),
    ('Experimental',(
        NODEBOOSTER_NG_CP_InterpolationInput,
        NODEBOOSTER_NG_CP_InterpolationMap,
        NODEBOOSTER_ND_CustomSocketUtility, ), #dev utility.
    ), 
    (NODEBOOSTER_NG_CP_MathExpression),
    (NODEBOOSTER_NG_CP_PyExpression),
    (NODEBOOSTER_NG_CP_PyNexScript),
    )

# for registration
classes = (
    NODEBOOSTER_SK_Interpolation,
    NODEBOOSTER_ND_CustomSocketUtility,
    NODEBOOSTER_NG_GN_CameraInfo,
    NODEBOOSTER_NG_SH_CameraInfo,
    NODEBOOSTER_NG_CP_CameraInfo,
    NODEBOOSTER_NG_GN_LightInfo,
    NODEBOOSTER_NG_SH_LightInfo,
    NODEBOOSTER_NG_CP_LightInfo,
    NODEBOOSTER_NG_GN_SceneInfo,
    NODEBOOSTER_NG_SH_SceneInfo,
    NODEBOOSTER_NG_CP_SceneInfo,
    NODEBOOSTER_NG_GN_RenderInfo,
    NODEBOOSTER_NG_SH_RenderInfo,
    NODEBOOSTER_NG_CP_RenderInfo,
    NODEBOOSTER_NG_GN_RNAInfo,
    NODEBOOSTER_NG_SH_RNAInfo,
    NODEBOOSTER_NG_CP_RNAInfo,
    NODEBOOSTER_NG_GN_IsRenderedView,
    NODEBOOSTER_NG_GN_SequencerSound,
    NODEBOOSTER_NG_SH_SequencerSound,
    NODEBOOSTER_NG_CP_SequencerSound,
    NODEBOOSTER_NG_GN_MathExpression,
    NODEBOOSTER_NG_SH_MathExpression,
    NODEBOOSTER_NG_CP_MathExpression,
    NODEBOOSTER_NG_GN_PyExpression,
    NODEBOOSTER_NG_SH_PyExpression,
    NODEBOOSTER_NG_CP_PyExpression,
    NODEBOOSTER_NG_GN_PyNexScript,
    NODEBOOSTER_NG_SH_PyNexScript,
    NODEBOOSTER_NG_CP_PyNexScript,
    NODEBOOSTER_NG_GN_DeviceInput,
    NODEBOOSTER_NG_SH_DeviceInput,
    NODEBOOSTER_NG_CP_DeviceInput,
    NODEBOOSTER_NG_GN_ObjectVelocity,
    NODEBOOSTER_NG_SH_ObjectVelocity,
    NODEBOOSTER_NG_CP_ObjectVelocity,
    NODEBOOSTER_NG_GN_InterpolationInput,
    NODEBOOSTER_NG_SH_InterpolationInput,
    NODEBOOSTER_NG_CP_InterpolationInput,
    NODEBOOSTER_NG_GN_InterpolationMap,
    NODEBOOSTER_NG_SH_InterpolationMap,
    NODEBOOSTER_NG_CP_InterpolationMap,
    NODEBOOSTER_OT_interpolation_input_update,
    )

#for utility. handlers.py module will use this list.
allcustomnodes = tuple(cls for cls in classes if
                  (('_NG_' in cls.__name__) or
                   ('_ND_' in cls.__name__)) )