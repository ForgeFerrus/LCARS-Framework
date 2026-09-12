"""
Enhanced Nova Act adapter (full-integration PoC):
- Asynchronous, non-blocking SDK import
- `connect(use_sdk=True)` performs background SDK init
- Exposes execute_action/list_devices/get_latest_telemetry
- Emits Nexus telemetry under `nova_act.telemetry`
"""
from __future__ import annotations
import importlib
import logging
import threading
import time
from typing import Any, Dict, Optional, Callable

from service.board_computer import TitaniumBoardComputer
from lcars.base.signal import Transmission 

logger =logging .getLogger ("lcars.plugins.nova_act")

_adapter =None 


class NovaActAdapter :
    """Adapter facade for Nova Act SDK with safe, optional SDK wiring.

    Key behaviours:
    - By default operates in simulated mode (fast, no SDK import).
    - If `connect(use_sdk=True)` is called (or `auto_connect` config), it
      attempts to import/instantiate the SDK in a background thread and will
      not block the caller/UI.
    - Telemetry is published into `kernel.nexus` under `nova_act.telemetry`.
    - Other components can retrieve the adapter via `lcars.plugins_impl.nova_act.get_adapter()`.
    """

    def __init__ (self ,computer =None ,config :Optional [dict ]=None ):
        self .computer =computer or get_computer ()
        self .config =config or {}
        self .connected =False # logical adapter availability
        self ._client =None # real SDK client or simulated placeholder
        self ._sdk_init_thread :Optional [threading .Thread ]=None 
        self ._sdk_ready =False 
        self ._running =False 
        self ._telemetry_thread :Optional [threading .Thread ]=None 
        self ._on_connect_callbacks :list [Callable ]=[]

        # ------------------ Connection / SDK wiring ------------------
    def connect (self ,use_sdk :bool =False ,blocking :bool =False ,timeout :float =5.0 )->bool :
        """Connect adapter. If use_sdk=True a background SDK init is scheduled.

        - blocking=True will wait up to `timeout` seconds for SDK init to finish.
        - Returns True when adapter is available (simulated or SDK).
        """
        if self .connected :
            return True 

        self .connected =True 
        # Start telemetry regardless (keeps UI informed)
        self ._start_telemetry ()

        if use_sdk :
        # Only attempt SDK import if explicitly allowed by env/config
            env_ok =os .getenv ("LCARS_NOVA_ACT_USE_SDK","0").lower ()in ("1","true")
            cfg_ok =bool (self .config .get ("use_sdk"))
            if env_ok or cfg_ok :
                self ._schedule_sdk_init ()
                if blocking :
                    return self .wait_for_sdk (timeout )
                return True 
            else :
                logger .info ('SDK import requested but disabled by env/config  staying in simulated mode')
        return True 

    def _schedule_sdk_init (self ):
        if self ._sdk_init_thread and self ._sdk_init_thread .is_alive ():
            return 

        def _init ():
            try :
                logger .info ("NovaActAdapter: attempting SDK import (background)")
                mod =importlib .import_module ("nova_act")
                client_cls =getattr (mod ,"Client",None )
                if client_cls :
                # Try to instantiate; prefer api_key from config if present
                    try :
                        api_key =self .config .get ("api_key")or os .getenv ("LCARS_NOVA_ACT_API_KEY")
                        if api_key :
                        # many SDK clients accept a token kwarg — attempt defensively
                            self ._client =client_cls (api_key )
                        else :
                            self ._client =client_cls ()
                    except Exception :
                    # Fallback: store module as client for manual calls
                        logger .warning ('Client class instantiation failed  storing module reference')
                        self ._client =mod 
                else :
                    self ._client =mod 

                self ._sdk_ready =True 
                logger .info ("NovaActAdapter: SDK ready")
                # Emit a UI event so panels can react
                try :
                    self .computer .event_bus .emit (Event (EventType .UI_COMPONENT_UPDATED ,"nova_act",{"status":"sdk_ready"}))
                except Exception :
                    pass 
            except Exception as e :
                logger .warning (f"NovaActAdapter: SDK import failed: {e}")
                self ._client =None 
                self ._sdk_ready =False 

        self ._sdk_init_thread =threading .Thread (target =_init ,daemon =True ,name ="nova-act-sdk-init")
        self ._sdk_init_thread .start ()

    def wait_for_sdk (self ,timeout :float =5.0 )->bool :
        """Wait for SDK init thread to complete (useful for tests).
        Returns True if SDK became ready within timeout.
        """
        if not self ._sdk_init_thread :
            return False 
        self ._sdk_init_thread .join (timeout =timeout )
        return self ._sdk_ready 

    def is_sdk_ready (self )->bool :
        return bool (self ._sdk_ready and self ._client )

    def disconnect (self )->None :
        self .connected =False 
        self ._sdk_ready =False 
        self ._client =None 
        self ._stop_telemetry ()

        # ------------------ Telemetry publishing ------------------
    def _start_telemetry (self ):
        if self ._running :
            return 
        self ._running =True 

        def _worker ():
            while self ._running :
                payload ={
                "ts":time .time (),
                "status":"connected"if self .connected else "disconnected",
                "sdk_ready":self .is_sdk_ready (),
                "metrics":{
                "voltage_v":round (28.0 +(time .time ()%1.0 ),2 ),
                "temperature_c":round (36.0 +(time .time ()%5.0 ),2 ),
                "rx_packets":int (time .time ())%1000 ,
                },
                }
                try :
                # Publish into Nexus shared memory
                    try :
                        self .computer .kernel .nexus .set_data ("nova_act.telemetry",payload )
                    except Exception :
                        self .computer .nexus .set_data ("nova_act.telemetry",payload )
                except Exception :
                    logger .exception ("Failed to publish NovaAct telemetry")
                time .sleep (1.5 )

        self ._telemetry_thread =threading .Thread (target =_worker ,daemon =True ,name ="nova-act-telemetry")
        self ._telemetry_thread .start ()

    def _stop_telemetry (self ):
        self ._running =False 
        if self ._telemetry_thread and self ._telemetry_thread .is_alive ():
            self ._telemetry_thread .join (timeout =0.5 )
        self ._telemetry_thread =None 

    def get_latest_telemetry (self )->Dict [str ,Any ]:
        try :
            return self .computer .kernel .nexus .get_data ("nova_act.telemetry",{})
        except Exception :
            return self .computer .nexus .get_data ("nova_act.telemetry",{})

            # ------------------ High-level API for BoardComputer/UI ------------------
    def list_devices (self )->list :
        """Return a list of devices/actuators known to the SDK or simulated set."""
        if self .is_sdk_ready ():
        # Defensive: try common attribute names
            client =self ._client 
            if hasattr (client ,"list_devices"):
                try :
                    return client .list_devices ()
                except Exception :
                    pass 
            if hasattr (client ,"get_devices"):
                try :
                    return client .get_devices ()
                except Exception :
                    pass 
                    # Simulated fallback
        return [{"id":"nova-1","type":"actuator","status":"nominal"}]

    def execute_action (self ,action :str ,params :Optional [dict ]=None )->Any :
        """Execute an action via SDK (if present) or simulate result.

        Returns SDK response or simulated dict.
        """
        params =params or {}
        if self .is_sdk_ready ():
            client =self ._client 
            # Try several common client entrypoints
            for name in ("execute","perform","send_action","run_action"):
                if hasattr (client ,name ):
                    try :
                        return getattr (client ,name )(action ,params )
                    except Exception as e :
                        logger .warning (f"NovaActAdapter: client.{name} failed: {e}")
                        # Last resort: if client is module, try attribute
            if hasattr (client ,action ):
                try :
                    return getattr (client ,action )(**params )
                except Exception :
                    pass 
                    # Simulated response
        return {"status":"simulated","action":action ,"params":params }


def setup (api ,config :Optional [dict ]=None ):
    """Plugin entrypoint called by the LCARS plugin loader."""
    global _adapter 
    comp =get_computer ()
    adapter =NovaActAdapter (comp ,config or {})
    _adapter =adapter 

    try :
        api .register_storage ("nova_act",adapter )
    except Exception :
        pass 

    try :
        ui_desc ={"panel":"lcars.ui.views.nova_act_panel:NovaActPanel","name":"Nova Act"}
        api .register_ui_integration (ui_desc )
    except Exception :
        pass 

        # If plugin config requests auto_connect, schedule non-blocking SDK init
    if config and config .get ("auto_connect"):
        adapter .connect (use_sdk =bool (config .get ("use_sdk",False )),blocking =False )

    logger .info ("Nova Act plugin initialized (adapter registered)")
    return adapter 


def get_adapter ()->Optional [NovaActAdapter ]:
    return _adapter 

