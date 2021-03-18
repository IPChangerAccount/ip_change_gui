from API_core.constants_change_ip import NEW_GATEWAY
import sys
import time

import platform
import subprocess
class NetworkHandler:

    SUBNET_MASK     = 'subnet_mask'
    LAN_IP_V4       = 'lan_ip_v4'
    DEFAULT_GATEWAY = 'default_gateway'
    
    WIN_OS = 'Windows'
    LIN_OS = 'Linux'
    
    DEFAULT_SYS_ENCODING = 'utf-8'
    _sys_encoding = None

    @classmethod
    def set_encoding(cls, encoding):
        cls._sys_encoding = encoding

    @classmethod
    def sys_encoding(cls):
        if cls._sys_encoding == None:
            return cls.DEFAULT_SYS_ENCODING
        else:
            return cls._sys_encoding

    @classmethod
    def _get_ethernet_name(cls):

        connection_name = None

        if platform.system() == cls.WIN_OS:

            WIN_INTERFACE_NAME_K_WORD = 'Interface Name'
            WIN_HEADER_ROW = 0
            WIN_FIRST_INTERFACE_ROW = 2

            # === Fetch and clear interfaces details ======================== #
            
            exec_result = subprocess.run(
                ['netsh', 'interface', 'show', 'interface'],
                stdout=subprocess.PIPE)
            

            exec_result = exec_result.stdout.decode(cls.sys_encoding()).strip()

            exec_result = exec_result.split('\r\n')
            # =============================================================== #

            # === Find name start pos ======================================= #
            header = exec_result[WIN_HEADER_ROW]
            name_st_pos = header.find(WIN_INTERFACE_NAME_K_WORD)
            # =============================================================== #
            

            first_interface_row = exec_result[WIN_FIRST_INTERFACE_ROW]
            connection_name = first_interface_row[name_st_pos:]
 
        elif platform.system() == cls.LIN_OS:
            
            # TODO handle Linux here
            
            pass

        else:

            # TODO log that unexpected platform was received
            pass

        # TODO Check if connection name was fetched. If not - raise exception.

        return connection_name

    @classmethod    
    def get_connection_details(cls):

        result = dict()
        
        target_conn_name = cls._get_ethernet_name()


        if platform.system() == cls.WIN_OS:

            WIN_ETHERNET_ADAPTER_K_WORD = 'Ethernet adapter '
            
            WIN_DEF_GATEWAY_K_WORK = 'Default Gateway'
            WIN_IPV4_ADDRES_K_WORD = 'IPv4 Address'
            WIN_SUBNET_MASK_K_WORD = 'Subnet Mask'

            # === Fetch and clear all ethernet connection details =========== #
            exec_result = subprocess.run(
                ['ipconfig'],
                stdout=subprocess.PIPE)
            exec_result = exec_result.stdout.decode(cls.sys_encoding()).strip()
           
            exec_result = exec_result.split(WIN_ETHERNET_ADAPTER_K_WORD)

            exec_result = exec_result[1:]
            # =============================================================== #

            # === Searching and cleaning target connection details ========== #
            for connection_details in exec_result:
                connection_details = connection_details.strip()
                connection_details = connection_details.split('\r\n')

                conn_name = connection_details[0][:-1] # skip":" char at the end

                if conn_name == target_conn_name:

                    for line in connection_details:
                        if WIN_DEF_GATEWAY_K_WORK in line:
                            result[cls.DEFAULT_GATEWAY] = \
                                line[line.find(':')+1:].strip() 

                        elif WIN_SUBNET_MASK_K_WORD in line:
                            result[cls.SUBNET_MASK] = \
                                line[line.find(':')+1:].strip() 

                        elif WIN_IPV4_ADDRES_K_WORD in line:
                            result[cls.LAN_IP_V4] = \
                                line[line.find(':')+1:].strip() 


                    break
            # =============================================================== #
 
        elif platform.system() == cls.LIN_OS:
            
            # TODO handle Linux here
            
            pass

        else:

            # TODO log that unexpected platform was received
            pass

        # TODO Check if all needed data was fetched. If not - raise exception.

        print (result)
        return result

    @classmethod
    def change_default_gateway(cls, new_gateway, conn_details : dict):
        changes_applied = False

        if platform.system() == cls.WIN_OS:
            WIN_RUN_AS_ADM_ERROR = \
             'the requested operation requires elevation (run as administrator)'


            # === Execute gateway change CMD ================================ #
            ip_change_cmd = [  'netsh', 'int', 'ip', 'set', 'address', 
                              f'"{cls._get_ethernet_name()}"',
                              f'address={conn_details[cls.LAN_IP_V4]}',
                              f'mask={conn_details[cls.SUBNET_MASK]}',
                              f'gateway={new_gateway}'
                            ]

            print(f'Going to change gateway using CMD {ip_change_cmd}')
            exec_result = subprocess.run(
                ip_change_cmd,
                stdout=subprocess.PIPE)

            exec_result = exec_result.stdout.decode(cls.sys_encoding()).strip()

            if WIN_RUN_AS_ADM_ERROR in exec_result.lower():
                print('Error! Please run the app as Administrator.')
                # TODO raise exception here ( or print) about the app should be
                # launched as admin.
                pass
            # =============================================================== #

            # === Verify changes ============================================ #
            RETRIES = 3

            retries_number = 0

            
            while retries_number <= RETRIES:
                time.sleep(3)

                retries_number +=1
                try:
                    new_details = cls.get_connection_details()
                    
                    new_ip   = new_details.get(cls.LAN_IP_V4)
                    new_mask = new_details.get(cls.SUBNET_MASK)
                    new_gate = new_details.get(cls.DEFAULT_GATEWAY)

                    if new_ip == None \
                      or new_ip != conn_details[cls.LAN_IP_V4]:
                        print(f'WARNING: incorrect LAN IP {new_ip} fetched')
                    
                    elif new_mask == None \
                      or new_mask != conn_details[cls.SUBNET_MASK]:
                        print(f'WARNING: incorrect Mask {new_mask} fetched')

                    elif new_gate == None \
                      or new_gate != new_gateway:
                        print(f'WARNING: incorrect fateway {new_gate} fetched')  

                    else:
                        changes_applied = True
                        break

                    print('Retrying...')

                except Exception as ex:
                    print(f'WARNING: ' 
                          + f'exception while get new connection details: {ex}')

            if not changes_applied:
                print(f'ERROR! IP Change FAILED! PLease contact support.')
                print(f'Change command result: {exec_result}')

            # =============================================================== #
 
        elif platform.system() == cls.LIN_OS:
            
            # TODO handle Linux here
            
            pass

        else:

            # TODO log that unexpected platform was received
            pass

        return changes_applied