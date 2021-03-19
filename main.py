import sys
import traceback
from threading import Thread

import PySimpleGUI as sg

from ip_operations import NetworkHandler
from processes_lock import ProcessesLock
from API_core.api_talker import ApiRequest

# === Main Layout Definition================================================= #
CHANGE_IP_BTN = 'Change IP'
TEXT_KEY      = '-GreetText-'
BTN_KEY       = '-ChangeIpBtn-'
OUTPUT_KEY    = '-ExecLog-'

text_object = sg.Text("Push below button to change external IP", key = TEXT_KEY)
change_ip_btn = sg.Button(CHANGE_IP_BTN, key = BTN_KEY)

horizontal_sep = sg.HorizontalSeparator(color = 'green')

exec_log_text = sg.Text("Execution log:")

output_window = sg.Output(echo_stdout_stderr = True, 
                         size=(90,20), 
                         key = OUTPUT_KEY)

layout = [[text_object], [change_ip_btn], 
          [horizontal_sep], 
          [exec_log_text], [output_window]]
# =========================================================================== #

# === App Already Running Layout Definition ================================= #
ERROR_KEY = 'EXIT'

already_exist_text = \
  sg.Text(
      'Application instance already running. Please use existing app instance.')

change_ip_btn = sg.Button(ERROR_KEY)

already_exist_layout = [[already_exist_text], [change_ip_btn]]
# =========================================================================== #

class State:
    ip_change_in_progress = None
    closing = None

    def __init__(self) -> None:
        self.ip_change_in_progress = False 
        self.closing = False

def change_ip(program_state : State):

    try:
        print('\n\nStarting get new IP procedure...')
        conn_details = NetworkHandler.get_connection_details()

        api_request = ApiRequest(conn_details[NetworkHandler.DEFAULT_GATEWAY])
        print('    Requesting new gateway...')
        new_gate = api_request.get_new_gate()
        print(f'    New gateway {new_gate} received. Applying...')
        

        if NetworkHandler.change_default_gateway(new_gate, conn_details):
            api_request.confirm_gate_usage_towards_api(new_gate)
            print('Success! IP changed.')
        else:
            # TODO Here send failed result to the gateway
            print('FAILED! Please contact support.')

    except Exception as ex:
        print(sys.exc_info()[0])
        print(traceback.format_exc())

        
        err_text = \
          f'\nAN ERROR OCCURRED! Error text: {str(ex)}. '\
           + '\nPlease contact support.\n'

        print(err_text)

    finally:
        if not state.closing: 
            program_state.ip_change_in_progress = False
            window.FindElement(BTN_KEY).Update(disabled=False)

def check_and_update_log_size(window):

    output_val = window.FindElement(OUTPUT_KEY).get()

    output_str_list = output_val.split('\n')

    if len(output_str_list) > 500:
        new_output_str_list = output_str_list[-500:]

        new_output_str = '\n'.join(new_output_str_list)

        window.FindElement(OUTPUT_KEY).update(value = new_output_str)

def display_app_already_exists():
    err_window = sg.Window("Application already launched.", 
                           already_exist_layout, 
                           margins=(25, 25))

    while True:

        event, values = err_window.read()

        if event == ERROR_KEY:
            break

        if event == sg.WIN_CLOSED:
            state.closing = True
            break

if __name__ == '__main__':
    
    THIS_APP_NAME = 'IP_CHANGE_GUI_APP'
    pr_lock = ProcessesLock(THIS_APP_NAME)

    lock_result = pr_lock.try_create_one_app_instance_lock()

    if lock_result != True:
        display_app_already_exists()
    
    else:    
        try:
            sys_encoding = sys.stdout.encoding
        
            NetworkHandler.set_encoding(sys_encoding)
            # Create the window
            window = sg.Window("IP Manager", layout, margins=(100, 25))
        
            state = State()
            ip_change_thread : Thread = None
        
            # Create an event loop
            while True:
                event, values = window.read()
                
                if event == BTN_KEY and not state.ip_change_in_progress:
        
                    check_and_update_log_size(window)
        
                    state.ip_change_in_progress = True    
                    window.FindElement(BTN_KEY).Update(disabled=True)
        
                    ip_change_thread = Thread(target = change_ip, 
                                              args = (state, ))
        
                    ip_change_thread.start()
            
                if event == sg.WIN_CLOSED:
                    state.closing = True
                    break
        
            if ip_change_thread.is_alive():
                ip_change_thread.join()
    
        finally:
            pr_lock.destroy_lock()
