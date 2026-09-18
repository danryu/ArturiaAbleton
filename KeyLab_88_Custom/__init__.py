from __future__ import absolute_import, print_function, unicode_literals
import _Framework.Capabilities as caps
from .KeyLab88Custom import KeyLab88Custom

def get_capabilities():
    return {
        caps.CONTROLLER_ID_KEY: caps.controller_id(
            vendor_id=7285,
            product_ids=[717],
            model_name=['KeyLab 88']
        ),
        caps.PORTS_KEY: [
            caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]),
            caps.outport(props=[caps.SCRIPT])
        ]
    }

def create_instance(c_instance):
    return KeyLab88Custom(c_instance)
